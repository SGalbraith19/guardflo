from tenancy.tier_policy import TIER_CAPABILITIES
from core.financial_rules import evaluate_financial_rules
from core.financial_explain import generate_explanation
from tenancy.audit import record_support_event


def run_financial_decision(request, organisation, policy):
   tier = organisation.tier
   capabilities = TIER_CAPABILITIES.get(tier)

   if not capabilities:
       raise ValueError(f"Unknown tier: {tier}")

   approved, risk_score, violations = evaluate_financial_rules(request, policy)

   explanation = None
   if capabilities.get("explainability"):
       explanation = generate_explanation(violations)

   if capabilities.get("audit_logging"):
       record_support_event({
           "event": "financial_decision",
           "organisation": organisation.name,
           "tier": tier,
           "approved": approved,
       })

   # 🔒 ALWAYS RETURN SAME SHAPE
   return {
       "approved": approved,
       "risk_score": risk_score,
       "violations": violations,
       "explanation": explanation,
   }