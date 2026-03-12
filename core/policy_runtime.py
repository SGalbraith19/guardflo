def evaluate(policy, request):

   violations = []
   risk = 0

   for rule in policy["rules"]:

       if rule["type"] == "amount_limit":
           if request["amount"] > rule["max"]:
               violations.append("amount_limit_exceeded")

       if rule["type"] == "block_category":
           if request["category"] == rule["value"]:
               violations.append("blocked_category")

       if rule["type"] == "risk_limit":
           if request.get("vendor_risk_score", 0) > rule["threshold"]:
               violations.append("risk_threshold_exceeded")

   return violations