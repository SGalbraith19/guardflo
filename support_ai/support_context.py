# support_ai/support_context.py

from typing import Dict

from support_ai.eligibility import evaluate_support_eligibility
from support_ai.pricing import get_pricing_band


def build_support_context(query: dict) -> Dict[str, str]:
   """
   Builds a deterministic, factual support context for the AI layer.

   This function:
   - does NOT infer intent
   - does NOT mutate state
   - does NOT negotiate
   - only reflects verified system facts
   """

   context: Dict[str, str] = {}

   # Base system disclosure (always present)
   context["system_context"] = (
       "This is an authoritative support system.\n"
       "All statements reflect system status at generation time.\n"
       "No guarantees, service levels, or obligations are implied unless "
       "explicitly stated in an executed support agreement."
   )

   # Pricing grounding (only when requested)
   if query.get("request_type") == "pricing":
       eligibility = evaluate_support_eligibility(
           declared_org_size=query.get("org_size"),
           production_instances=query.get("production_instances"),
           critical_path=query.get("critical_path"),
           audit_exposure=query.get("audit_exposure"),
       )

       if not eligibility.eligible:
           context["pricing_context"] = (
               "Support pricing could not be determined because the provided "
               "organisation details are inconsistent.\n\n"
               f"Required organisation classification: {eligibility.enforced_org_size}.\n"
               "Support guarantees are issued only after eligibility verification."
           )
       else:
           band = get_pricing_band(eligibility.enforced_org_size)
           context["pricing_context"] = (
               "Indicative Support Tier:\n"
               f"Organisation Size: {band.intended_org_size}\n"
               f"Annual Range (USD): {band.annual_range_usd}\n"
               f"Notes: {band.notes}\n\n"
               "Pricing is indicative only and subject to an executed support agreement."
           )

   return context