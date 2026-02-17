from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4
import hashlib
import json
import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Database
from database import get_db

# Models
from tenancy.models import Organisation
from models.financial_ledger import FinancialLedger
from models.policy_registry import PolicyRegistry

# Core enforcement
from core.decision_engine import run_financial_decision
from core.signing import sign_decision, verify_signature
from core.financial_schema import (
   FinancialDecisionRequest,
   FinancialDecisionResponse,
)

# Billing
from billing.billing import get_monthly_usage, create_checkout_session
from tenancy.tier_policy import TIER_LIMITS
from tenancy.service import resolve_organisation


load_dotenv()

app = FastAPI(title="GuardFlo Financial Enforcement Gate")

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
   return {"status": "Financial enforcement API live"}


# ============================================================
# RATE LIMITING
# ============================================================

def tenant_key(request: Request):
   return request.headers.get("x-api-key", get_remote_address(request))


limiter = Limiter(key_func=tenant_key)
app.state.limiter = limiter


app.add_exception_handler(
   RateLimitExceeded,
   lambda request, exc: JSONResponse(
       status_code=429,
       content={"detail": "Rate limit exceeded"},
   ),
)

# ============================================================
# FINANCIAL DECISION ENDPOINT
# ============================================================

@app.post("/decision/financial", response_model=FinancialDecisionResponse)
def financial_decision(
   request: FinancialDecisionRequest,
   db: Session = Depends(get_db),
):

   organisation = resolve_organisation(request.tenant_id)

   if not organisation or not organisation.subscription_active:
       raise HTTPException(status_code=403, detail="Subscription inactive")

   # Tier enforcement
   tier_limits = TIER_LIMITS.get(organisation.tier)

   if tier_limits and tier_limits.get("monthly_decisions"):
       usage = get_monthly_usage(organisation.name)
       if usage >= tier_limits["monthly_decisions"]:
           raise HTTPException(
               status_code=403,
               detail="Monthly decision limit exceeded",
           )

   # Lock policy version
   policy = (
       db.query(PolicyRegistry)
       .filter(PolicyRegistry.version == request.policy_version)
       .first()
   )

   if not policy:
       raise HTTPException(status_code=400, detail="Invalid policy version")

   result = run_financial_decision(request, organisation, policy)

   decision_id = str(uuid4())
   timestamp = datetime.utcnow().isoformat()

   decision_payload = {
       "decision_id": decision_id,
       "tenant_id": request.tenant_id,
       "policy_version": policy.version,
       "timestamp": timestamp,
       "decision": result["decision"],
       "reason_codes": result["reason_codes"],
   }

   signature = sign_decision(decision_payload)
   decision_payload["signature"] = signature

   # ============================================================
   # HASH CHAIN LEDGER
   # ============================================================

   request_hash = hashlib.sha256(
       json.dumps(request.dict(), sort_keys=True).encode()
   ).hexdigest()

   previous_entry = (
       db.query(FinancialLedger)
       .filter(FinancialLedger.tenant_id == request.tenant_id)
       .order_by(FinancialLedger.created_at.desc())
       .first()
   )

   previous_hash = previous_entry.entry_hash if previous_entry else None

   entry_string = json.dumps(
       {
           "tenant_id": request.tenant_id,
           "policy_version": policy.version,
           "request_hash": request_hash,
           "decision": result["decision"],
           "signature": signature,
           "previous_hash": previous_hash,
       },
       sort_keys=True,
   )

   entry_hash = hashlib.sha256(entry_string.encode()).hexdigest()

   ledger_entry = FinancialLedger(
       id=decision_id,
       tenant_id=request.tenant_id,
       policy_version=policy.version,
       request_hash=request_hash,
       decision=result["decision"],
       signature=signature,
       previous_hash=previous_hash,
       entry_hash=entry_hash,
   )

   db.add(ledger_entry)
   db.commit()

   return FinancialDecisionResponse(**decision_payload)


# ============================================================
# SIGNATURE VERIFICATION ENDPOINT
# ============================================================

@app.post("/verify-signature")
def verify_decision_signature(data: dict = Body(...)):
   signature = data.pop("signature", None)

   if not signature:
       raise HTTPException(status_code=400, detail="Missing signature")

   valid = verify_signature(data, signature)

   return {"valid": valid}


# ============================================================
# LEDGER INTEGRITY VALIDATION
# ============================================================

@app.get("/ledger/validate/{tenant_id}")
def validate_ledger(tenant_id: str, db: Session = Depends(get_db)):

   entries = (
       db.query(FinancialLedger)
       .filter(FinancialLedger.tenant_id == tenant_id)
       .order_by(FinancialLedger.created_at.asc())
       .all()
   )

   previous_hash = None

   for entry in entries:

       entry_string = json.dumps(
           {
               "tenant_id": entry.tenant_id,
               "policy_version": entry.policy_version,
               "request_hash": entry.request_hash,
               "decision": entry.decision,
               "signature": entry.signature,
               "previous_hash": entry.previous_hash,
           },
           sort_keys=True,
       )

       computed_hash = hashlib.sha256(entry_string.encode()).hexdigest()

       if computed_hash != entry.entry_hash:
           return {"valid": False, "error": "Ledger tampering detected"}

       if entry.previous_hash != previous_hash:
           return {"valid": False, "error": "Broken hash chain"}

       previous_hash = entry.entry_hash

   return {"valid": True}