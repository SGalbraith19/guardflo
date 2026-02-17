from tenancy.tier_policy import TIER_CAPABILITIES
from core.financial_rules import evaluate_financial_rules
from core.financial_explain import generate_explanation
from tenancy.audit import record_support_event


def run_financial_decision(request, organisation):
   tier = organisation.tier
   capabilities = TIER_CAPABILITIES.get(tier)

   if not capabilities:
       raise ValueError(f"Unknown tier: {tier}")

   approved, risk_score, violations = evaluate_financial_rules(request)

   response = {
       "approved": approved,
   }

   if capabilities["risk_scoring"]:
       response["risk_score"] = risk_score
       response["violations"] = violations

   if capabilities["explainability"]:
       response["explanation"] = generate_explanation(violations)

   if capabilities["audit_logging"]:
       record_support_event({
           "event": "financial_decision",
           "organisation": organisation.name,
           "tier": tier,
           "approved": approved,
       })

   return response