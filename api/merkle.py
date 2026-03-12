from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.financial_ledger import FinancialLedger
from core.merkle import compute_merkle_root

router = APIRouter(prefix="/ledger", tags=["ledger"])


@router.get("/merkle-root")
def merkle_root(db: Session = Depends(get_db)):
   entries = (
       db.query(FinancialLedger)
       .order_by(FinancialLedger.id.asc())
       .all()
   )

   hashes = [e.decision_hash for e in entries]

   root = compute_merkle_root(hashes)

   from core.ledger_anchor import anchor_merkle_root
   anchor_merkle_root(root)

   return {
       "entries": len(hashes),
       "merkle_root": root,
   }