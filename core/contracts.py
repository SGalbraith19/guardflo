# support_ai/contract.py

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SupportTier:
   name: str
   annual_price_usd: int
   uptime_guarantee: str
   audit_retention: str
   incident_response: str
   notes: str


SUPPORTED_TIERS: Dict[str, SupportTier] = {
   "community": SupportTier(
       name="Community",
       annual_price_usd=0,
       uptime_guarantee="None",
       audit_retention="Best-effort, no guarantees",
       incident_response="None",
       notes="Intended for evaluation and non-critical usage."
   ),
   "standard": SupportTier(
       name="Standard",
       annual_price_usd=10000,
       uptime_guarantee="99.5%",
       audit_retention="90 days",
       incident_response="Best-effort during business hours",
       notes="For small teams running enforcement in production."
   ),
   "enterprise": SupportTier(
       name="Enterprise",
       annual_price_usd=25000,
       uptime_guarantee="99.9%",
       audit_retention="12 months",
       incident_response="Guaranteed response window",
       notes="For critical-path usage with compliance requirements."
   ),
}

# support_ai/contract_context.py

from core.contracts import SUPPORTED_TIERS


def build_contract_context() -> str:
   """
   Builds a factual description of contractual boundaries.
   Injected verbatim into the AI context.
   """

   lines = []

   lines.append("Contractual Boundary:\n")

   for tier in SUPPORTED_TIERS.values():
       lines.append(f"Tier: {tier.name}")
       lines.append(f"Annual Pricing: {tier.annual_range_usd}")
       lines.append(f"Uptime Guarantee: {tier.uptime_guarantee}")
       lines.append(f"Audit Retention: {tier.audit_retention}")
       lines.append(f"Incident Response: {tier.incident_response}")
       lines.append(f"Notes: {tier.notes}")
       lines.append("")

   lines.append(
       "Guarantees, service levels, and obligations are valid "
       "only under a formally executed support agreement. "
       "No guarantees are implied through system usage alone."
   )

   return "\n".join(lines)