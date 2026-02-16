from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
from sqlalchemy import func
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from support_ai.database import SessionLocal
from support_ai.models import FinancialDecision, Organisation
from support_ai.engine.decision_engine import run_financial_decision
from support_ai.engine.tier_policy import TIER_LIMITS
from support_ai.tenancy import resolve_organisation
from support_ai.financial_schema import FinancialDecisionRequest, FinancialDecisionResponse
from support_ai.billing import get_monthly_usage, create_checkout_session

load_dotenv()

app = FastAPI(title="GuardFlo Authoritative Support Surface")
@app.get("/")
def root():
    return {"status": "API is live"}

# =============================
# Rate Limiting Setup
# =============================

def tenant_key(request: Request):
   return request.headers.get("x-api-key", "anonymous")

limiter = Limiter(key_func=tenant_key)
app.state.limiter = limiter

app.add_exception_handler(
   RateLimitExceeded,
   lambda request, exc: JSONResponse(
       status_code=429,
       content={"detail": "Rate limit exceeded"},
   ),
)

# =============================
# FINANCIAL DECISION ENDPOINT
# =============================

@app.post("/decision/financial", response_model=FinancialDecisionResponse)
def financial_decision(request: FinancialDecisionRequest):

   organisation = resolve_organisation(request.tenant_id)

   if not organisation or not organisation.subscription_active:
       raise HTTPException(
           status_code=403,
           detail="Subscription inactive"
       )

   # Tier enforcement
   tier_limits = TIER_LIMITS.get(organisation.tier)

   if tier_limits and tier_limits.get("monthly_decisions"):
       usage = get_monthly_usage(organisation.name)

       if usage >= tier_limits["monthly_decisions"]:
           raise HTTPException(
               status_code=403,
               detail="Monthly decision limit exceeded"
           )

   # Run core logic
   result = run_financial_decision(request, organisation)

   decision_id = str(uuid4())
   timestamp = datetime.utcnow()

   # Persist decision
   db = SessionLocal()
   try:
       decision = FinancialDecision(
           id=decision_id,
           organisation=organisation.name,
           approved=result["approved"],
           risk_score=result["risk_score"],
           violations=result["violations"],
           explanation=result["explanation"],
           created_at=timestamp,
       )

       db.add(decision)
       db.commit()
   finally:
       db.close()

   return FinancialDecisionResponse(
       decision_id=decision_id,
       timestamp=timestamp,
       **result
   )

# =============================
# BILLING CHECKOUT ENDPOINT
# =============================

@app.post("/billing/checkout")
def start_checkout(data: dict = Body(...)):

   tier = data.get("tier")
   organisation_name = data.get("organisation")

   price_map = {
       "starter": 4900,
       "pro": 19900,
       "enterprise": 99900,
   }

   amount = price_map.get(tier)

   if not amount:
       raise HTTPException(status_code=400, detail="Invalid tier")

   checkout_url = create_checkout_session(
       amount,
       organisation_name
   )

   return {"checkout_url": checkout_url}