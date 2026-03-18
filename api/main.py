from concurrent.futures import ThreadPoolExecutor
import json
import hashlib
import logging
import uuid
from uuid import uuid4
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from requests import request
from sqlalchemy.orm import Session
from sqlalchemy import func, create_engine

from dotenv import load_dotenv
from pathlib import Path

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fastapi.middleware.cors import CORSMiddleware

from tenancy.models import Base
from tenancy.models import Organisation
from tenancy.service import resolve_organisation
from tenancy.tier_policy import TIER_CAPABILITIES

from database import get_db, engine

from models.financial_ledger import FinancialLedger
from models.policy_registry import PolicyRegistry

from core.decision_engine import run_financial_decision
from core.metrics import decision_counter, decision_denied
from core.signing import sign_decision, verify_signature

from core.financial_schema import (
   FinancialDecisionRequest,
   FinancialDecisionResponse,
)

from billing.usage_meter import increment_usage_atomic
from api.replay import router as replay_router
from api.usage import enforce_usage
from billing.stripe_service import router as stripe_router

ENGINE_VERSION ="1.1.0"


# ------------------------------------------------
# INIT
# ------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="GuardFlo Financial Enforcement Gate")


# ------------------------------------------------
# STRIPE + ROUTERS
# ------------------------------------------------

app.include_router(stripe_router)
app.include_router(replay_router)


# ------------------------------------------------
# STATIC + TEMPLATES
# ------------------------------------------------

templates = Jinja2Templates(directory="templates")

app.mount(
   "/static",
   StaticFiles(directory="static"),
   name="static"
)


# ------------------------------------------------
# CORS MIDDLEWARE
# ------------------------------------------------

app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)


# ------------------------------------------------
# RATE LIMITING
# ------------------------------------------------

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
   return JSONResponse(
       status_code=429,
       content={"detail": "Rate limit exceeded"},
   )


# ------------------------------------------------
# STARTUP
# ------------------------------------------------

@app.on_event("startup")
def startup():
   Base.metadata.create_all(bind=engine)


# ---------------------------------------------------
# MERKLE ROOT
# ---------------------------------------------------

def compute_merkle_root(hashes):

   if not hashes:
       return None

   level = hashes[:]

   while len(level) > 1:

       next_level = []

       for i in range(0, len(level), 2):

           left = level[i]
           right = level[i + 1] if i + 1 < len(level) else left

           combined = hashlib.sha256(
               (left + right).encode()
           ).hexdigest()

           next_level.append(combined)

       level = next_level

   return level[0]


# ---------------------------------------------------
# DETERMINISTIC POLICY VM
# ---------------------------------------------------

def run_policy_vm(request, organisation, policy):

   context = {
       "amount": request.amount,
       "vendor_risk": request.vendor_risk_score,
       "duplicate": request.duplicate_flag,
       "chain_depth": request.approval_chain_depth
   }

   violations = []
   risk_score = 0

   for rule in policy.rules:

       rule_type = rule.get("type")

       if rule_type == "max_amount":

           if context["amount"] > rule["value"]:
               violations.append("amount_exceeds_limit")

       elif rule_type == "vendor_risk":

           if context["vendor_risk"] > rule["value"]:
               violations.append("vendor_risk_high")

       elif rule_type == "duplicate":

           if context["duplicate"]:
               violations.append("duplicate_transaction")

       elif rule_type == "chain_depth":

           if context["chain_depth"] > rule["value"]:
               violations.append("approval_chain_too_deep")

   if context["amount"] > 10000:
       risk_score += 30

   if context["vendor_risk"] > 7:
       risk_score += 40

   approved = len(violations) == 0

   return {
       "approved": approved,
       "violations": violations,
       "risk_score": risk_score,
       "explanation": "deterministic_policy_vm"
   }


# ---------------------------------------------------
# FINANCIAL DECISION
# ---------------------------------------------------

@app.post("/api/v1/decide", response_model=FinancialDecisionResponse)
def financial_decision(
   request: FinancialDecisionRequest,
   x_api_key: str = Header(...),
   idempotency_key: str = Header(...),
   db: Session = Depends(get_db),
):

   organisation = resolve_organisation(api_key=x_api_key, db=db)

   if not organisation:
       raise HTTPException(404, "Organisation not found")

   if not organisation.subscription_active:
       raise HTTPException(403, "Subscription inactive")

   tenant_id = organisation.id

   ai_override = False
   ai_violation = None

   if request.actor_type == "ai_agent" and request.approval_chain_depth < 1:
    ai_override = True
    ai_violation = "ai_agent_payment_blocked"

   try:

       # -----------------------------
       # REQUEST HASH
       # -----------------------------

       request_hash = hashlib.sha256(
           json.dumps(request.dict(), sort_keys=True, default=str).encode()
       ).hexdigest()

       # -----------------------------
       # DETERMINISTIC DECISION ID
       # -----------------------------

       decision_id = hashlib.sha256(
           f"{tenant_id}:{request_hash}:{request.nonce}".encode()
       ).hexdigest()

       # -----------------------------
       # IDEMPOTENCY CHECK
       # -----------------------------

       existing = (
           db.query(FinancialLedger)
           .filter(
               FinancialLedger.idempotency_key == idempotency_key,
               FinancialLedger.organisation_id == tenant_id
           )
           .first()
       )

       if existing:

           return FinancialDecisionResponse(
               decision_id=str(existing.id),
               tenant_id=str(existing.organisation_id),
               policy_version=existing.policy_version,
               timestamp=datetime.utcnow().isoformat(),
               approved=existing.decision,
               risk_score=0,
               violations=[],
               explanation="replayed request",
               signature=existing.signature
           )

       # -----------------------------
       # NONCE PROTECTION
       # -----------------------------

       nonce_exists = (
           db.query(FinancialLedger)
           .filter(
               FinancialLedger.nonce == str(request.nonce),
               FinancialLedger.organisation_id == tenant_id
           )
           .first()
       )

       if nonce_exists:
           raise HTTPException(409, "Nonce already used")

       # -----------------------------
       # ANOMALY DETECTION
       # -----------------------------

       recent = (
           db.query(func.count(FinancialLedger.id))
           .filter(
               FinancialLedger.organisation_id == tenant_id,
               FinancialLedger.created_at >
               datetime.utcnow() - timedelta(minutes=1)
           )
           .scalar()
       )

       if recent > 50:
           raise HTTPException(429, "Anomalous request burst detected")

       # -----------------------------
       # QUOTA CHECK
       # -----------------------------

       tier_limits = TIER_CAPABILITIES.get(organisation.tier)

       if not tier_limits:
           raise HTTPException(400, "Unknown tier")

       monthly_limit = tier_limits.get("monthly_decisions")

       first_of_month = datetime.utcnow().replace(
           day=1, hour=0, minute=0, second=0, microsecond=0
       )

       monthly_count = (
           db.query(func.count(FinancialLedger.id))
           .filter(
               FinancialLedger.organisation_id == tenant_id,
               FinancialLedger.created_at >= first_of_month
           )
           .scalar()
       )

       if monthly_limit and monthly_count >= monthly_limit:
           raise HTTPException(403, "Monthly decision limit exceeded")

       # -----------------------------
       # FETCH POLICY
       # -----------------------------

       policy = (
           db.query(PolicyRegistry)
           .filter(PolicyRegistry.version == str(request.policy_version))
           .first()
       )

       if not policy:
           raise HTTPException(404, "Policy version not found")

       policy_hash = policy.policy_hash

       # -----------------------------
       # RUN POLICY VM
       # -----------------------------

       with ThreadPoolExecutor() as executor:

           future = executor.submit(
               run_policy_vm,
               request,
               organisation,
               policy
           )

           result = future.result()

       timestamp = datetime.utcnow().isoformat()

       decision_payload = {
           "decision_id": decision_id,
           "tenant_id": str(organisation.id),
           "policy_version": request.policy_version,
           "engine_version": ENGINE_VERSION,
           "timestamp": timestamp,
           "approved": approved,
           "risk_score": risk_score,
           "violations": violations,
           "explanation": result["explanation"],
       }

       if ai_override:
           approved = False
           risk_score = max(risk_score,90)
           violations = violations + [ai_violation]

       signature = sign_decision(decision_payload)
       decision_payload["signature"] = signature

       # -----------------------------
       # HASH CHAIN
       # -----------------------------

       previous_entry = (
           db.query(FinancialLedger)
           .filter(FinancialLedger.organisation_id == tenant_id)
           .order_by(FinancialLedger.created_at.desc())
           .first()
       )

       previous_hash = (
           previous_entry.entry_hash if previous_entry else "GENESIS"
       )

       entry_string = json.dumps(
           {
               "id": decision_id,
               "organisation_id": str(tenant_id),
               "request_hash": request_hash,
               "decision": result["approved"],
               "signature": signature,
               "previous_hash": previous_hash
           },
           sort_keys=True
       )

       entry_hash = hashlib.sha256(entry_string.encode()).hexdigest()

       # -----------------------------
       # MERKLE ROOT
       # -----------------------------

       recent_hashes = [
           e.entry_hash
           for e in db.query(FinancialLedger.entry_hash)
           .filter(FinancialLedger.organisation_id == tenant_id)
           .order_by(FinancialLedger.created_at.desc())
           .limit(100)
       ]

       merkle_root = compute_merkle_root(recent_hashes + [entry_hash])

       # -----------------------------
       # LEDGER WRITE
       # -----------------------------

       ledger_entry = FinancialLedger(

           id=uuid.uuid4(),
           organisation_id=tenant_id,
           policy_version=policy.version,
           engine_version="1.1.0",

           decision=result["approved"],

           request_hash=request_hash,
           nonce=request.nonce,
           idempotency_key=idempotency_key,

           signature=signature,

           previous_hash=previous_hash,
           entry_hash=entry_hash,
           merkle_root=merkle_root
       )

       db.add(ledger_entry)
       db.commit()

       logger.info(
           f"decision_created tenant={tenant_id} decision_id={decision_id}"
       )

       return FinancialDecisionResponse(**decision_payload)

   except HTTPException:
       raise

   except Exception as e:

       logger.exception("Decision failure")

       raise HTTPException(
           500,
           f"Atomic enforcement failure: {str(e)}"
       )
       

# ---------------------------------------------------
# SIGNATURE VERIFICATION
# ---------------------------------------------------

@app.post("/decision/verify")
def verify_decision(decision_id: str, signature: str, db: Session = Depends(get_db)):

   decision = (
       db.query(FinancialLedger)
       .filter(FinancialLedger.id == decision_id)
       .first()
   )

   if not decision:
       raise HTTPException(404, "Decision not found")

   payload = {
       "decision_id": str(decision.id),
       "tenant_id": str(decision.organisation_id),
       "policy_version": decision.policy_version,
       "approved": decision.decision
   }

   valid = verify_signature(payload, signature)

   return {"decision_id": decision_id, "valid": valid}


# ---------------------------------------------------
# LEDGER VALIDATION
# ---------------------------------------------------

@app.get("/ledger/validate/{tenant_id}")
def validate_ledger(tenant_id: str, db: Session = Depends(get_db)):

   entries = (
       db.query(FinancialLedger)
       .filter(FinancialLedger.organisation_id == tenant_id)
       .order_by(FinancialLedger.created_at.asc())
       .all()
   )

   previous_hash = None

   for entry in entries:

       entry_string = json.dumps(
           {
               "id": str(entry.id),
               "organisation_id": str(entry.organisation_id),
               "request_hash": entry.request_hash,
               "decision": entry.decision,
               "signature": entry.signature,
               "previous_hash": entry.previous_hash
           },
           sort_keys=True
       )

       computed_hash = hashlib.sha256(entry_string.encode()).hexdigest()

       if computed_hash != entry.entry_hash:
           return {"valid": False, "error": f"Hash mismatch at {entry.id}"}

       if previous_hash and entry.previous_hash != previous_hash:
           return {"valid": False, "error": f"Chain broken at {entry.id}"}

       previous_hash = entry.entry_hash

   return {
       "valid": True,
       "entries_checked": len(entries)
   }

# =========================================
# UI ROUTES
# =========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
   return templates.TemplateResponse(
       "platform.html",
       {"request": request}
   )


@app.get("/platform", response_class=HTMLResponse)
async def platform(request: Request):
   return templates.TemplateResponse(
       "platform.html",
       {"request": request}
   )


@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
   return templates.TemplateResponse(
       "pricing.html",
       {"request": request}
   )


@app.get("/security", response_class=HTMLResponse)
async def security(request: Request):
   return templates.TemplateResponse(
       "security.html",
       {"request": request}
   )


@app.get("/enterprise", response_class=HTMLResponse)
async def enterprise(request: Request):
   return templates.TemplateResponse(
       "enterprise.html",
       {"request": request}
   )


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
   return templates.TemplateResponse(
       "terms.html",
       {"request": request}
   )


@app.get("/documentation", response_class=HTMLResponse)
async def documentation(request: Request):
   return templates.TemplateResponse(
       "documentation.html",
       {"request": request}
   )


@app.get("/success", response_class=HTMLResponse)
async def success(request: Request):
   return templates.TemplateResponse(
       "success.html",
       {"request": request}
   )

@app.get("/architecture", response_class=HTMLResponse)
async def architecture(request: Request):
   return templates.TemplateResponse(
       "architecture.html",
       {"request": request}
   )