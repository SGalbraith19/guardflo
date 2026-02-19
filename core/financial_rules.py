from typing import List, Tuple


MAX_AUTO_APPROVAL_AMOUNT = 10000
MAX_VENDOR_RISK = 0.7
MAX_APPROVAL_DEPTH = 2
MAX_FAN_OUT = 5


def evaluate_financial_rules(request, policy):

   violations = []
   risk_score = 0

   # Amount risk
   if request.amount > MAX_AUTO_APPROVAL_AMOUNT:
       risk_score += 40
       violations.append("High amount")

   # Vendor risk
   risk_score += request.vendor_risk_score * 30

   # Duplicate risk
   if request.duplicate_flag:
       risk_score += 25
       violations.append("Duplicate invoice detected")

   # Approval chain depth
   if request.approval_chain_depth < 2:
       risk_score += 20
       violations.append("Insufficient approval depth")

   approved = risk_score < 60

   return approved, risk_score, violations