from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.financial_ledger import FinancialLedger
from core.decision_engine import run_financial_decision

router = APIRouter()


@router.get("/decision/replay/{decision_id}")
def replay(decision_id: str, db: Session = Depends(get_db)):

   entry = db.query(FinancialLedger).filter(
       FinancialLedger.id == decision_id
   ).first()

   if not entry:
       raise HTTPException(status_code=404, detail="Decision not found")

   # recompute the decision deterministically
   recomputed = run_financial_decision(
       entry.request_data,
       entry.organisation_id,
       entry.policy_version
   )

   valid = recomputed["request_hash"] == entry.request_hash

   return {
       "decision_id": decision_id,
       "valid": valid
   }