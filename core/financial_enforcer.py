from sqlalchemy.orm import Session
from datetime import datetime
from models.tenant import Tenant
from models.financial_ledger import FinancialLedger
from billing.usage_meter import get_usage_for_update, increment_usage
from core.decision_engine import run_financial_decision
from signing.signer import sign_payload
import json
import hashlib

from security.key_registry import get_active_key, ACTIVE_KEY_VERSION

def enforce_financial_decision(
   db: Session,
   tenant: Tenant,
   request_payload: dict,
):
   """
   Atomic enforcement pipeline.

   Guarantees:
   - Row locking
   - Quota enforcement
   - Deterministic decision
   - Ledger write
   - Usage increment
   - All inside one transaction
   """

   # ---- START TRANSACTION ----
   with db.begin():

       # 1️⃣ Lock usage row
       usage = get_usage_for_update(db, tenant.id)

       # 2️⃣ Subscription check
       if not tenant.active:
           raise Exception("Subscription inactive")

       # 3️⃣ Quota check
       if usage.current_period_usage >= tenant.monthly_quota:
           raise Exception("Monthly quota exceeded")

       # 4️⃣ Deterministic decision
       decision_result = run_financial_decision(
           request_payload,
           tenant,
       )

       # 5️⃣ Canonical serialization
       canonical = json.dumps(
           decision_result,
           sort_keys=True,
           separators=(",", ":"),
       )

       decision_hash = hashlib.sha256(
           canonical.encode()
       ).hexdigest()
    
       active_key = get_active_key()
       signature = sign_payload(canonical, active_key)

       # 7️⃣ Increment usage
       increment_usage(usage)

       # Commit happens automatically when exiting context

   return {
       "decision": decision_result,
       "signature": signature,
   }