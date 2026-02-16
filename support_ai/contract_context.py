# support_ai/contract_context.py

from support_ai.contracts import SUPPORTED_TIERS


def build_contract_context() -> str:
   """
   Builds a factual description of available support tiers.
   This is injected into the AI context verbatim.
   """

   lines = []
   lines.append("Available Support Tiers:\n")

   for tier in SUPPORTED_TIERS.values():
       lines.append(f"Tier: {tier.name}")
       lines.append(f"Annual Price (USD): {tier.annual_price_usd}")
       lines.append(f"Uptime Guarantee: {tier.uptime_guarantee}")
       lines.append(f"Audit Retention: {tier.audit_retention}")
       lines.append(f"Incident Response: {tier.incident_response}")
       lines.append(f"Notes: {tier.notes}")
       lines.append("")  # blank line between tiers

   return "\n".join(lines)