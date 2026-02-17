import uuid
from datetime import datetime
from typing import Dict, Any, List

def evaluate_transaction(
   transaction: Dict[str, Any],
   policy: Dict[str, Any],
   daily_total: float
) -> Dict[str, Any]:

   reasons: List[str] = []

   amount = transaction["amount"]
   category = transaction.get("category")
   risk_score = transaction.get("risk_score", 0)

   # 1. Per-transaction limit
   if amount > policy["max_transaction_amount"]:
       reasons.append("MAX_TRANSACTION_EXCEEDED")

   # 2. Daily cumulative limit
   if (daily_total + amount) > policy["max_daily_amount"]:
       reasons.append("MAX_DAILY_LIMIT_EXCEEDED")

   # 3. Risk score threshold
   if risk_score > policy["max_risk_score"]:
       reasons.append("RISK_SCORE_EXCEEDED")

   # 4. Disallowed category
   if category in policy["blocked_categories"]:
       reasons.append("CATEGORY_BLOCKED")

   decision = "deny" if reasons else "allow"

   return {
       "decision": decision,
       "reason_codes": reasons,
   }