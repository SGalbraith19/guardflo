from database import SessionLocal
from models.financial_ledger import FinancialLedger


def append_ledger(entry: FinancialLedger):
   session = SessionLocal()
   try:
       session.add(entry)
       session.commit()
   finally:
       session.close()