import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

from tenancy.models import Organisation
from tenancy.repository import SessionLocal


# ============================================================
# Deployment Mode
# ============================================================

DEPLOYMENT_MODE = os.getenv("GUARDFLO_MODE", "multi")  # multi | dedicated


# ============================================================
# Pricing Model
# ============================================================

@dataclass
class PricingInput:
   organisation_size: str  # small | medium | large
   production: bool = False
   sla_24_7: bool = False
   priority_response: bool = False
   dedicated_channel: bool = False
   custom_clauses: bool = False


BASE_PRICING = {
   "small": 10000,
   "medium": 25000,
   "large": 50000,
}


def calculate_pricing(input: PricingInput) -> Dict[str, Any]:
   if input.organisation_size not in BASE_PRICING:
       raise ValueError("Invalid organisation size")

   base = BASE_PRICING[input.organisation_size]
   total = base
   multipliers = []

   if input.production:
       total *= 1.20
       multipliers.append("Production +20%")

   if input.sla_24_7:
       total *= 1.15
       multipliers.append("24/7 SLA +15%")

   if input.priority_response:
       total *= 1.10
       multipliers.append("Priority Response +10%")

   if input.dedicated_channel:
       total *= 1.10
       multipliers.append("Dedicated Channel +10%")

   if input.custom_clauses:
       total *= 1.10
       multipliers.append("Custom Clauses +10%")

   total = round(total, -2)  # round to nearest 100

   return {
       "base_price": base,
       "final_price": total,
       "applied_multipliers": multipliers,
   }


# ============================================================
# Organisation Resolution
# ============================================================

def resolve_organisation(api_key: str) -> Optional[Organisation]:
   """
   Resolves organisation from API key.
   Handles dedicated vs multi-tenant mode.
   """

   if DEPLOYMENT_MODE == "dedicated":
       return Organisation(
           org_id=os.getenv("GUARDFLO_ORG_ID", "org_dedicated"),
           org_name=os.getenv("GUARDFLO_ORG_NAME", "DedicatedEnterprise"),
           tier=os.getenv("GUARDFLO_ORG_TIER", "enterprise"),
           api_key="dedicated",
           active=True,
           subscription_active=True,
       )

   db = SessionLocal()
   try:
       org = (
           db.query(Organisation)
           .filter(Organisation.api_key == api_key)
           .first()
       )

       if not org:
           return None

       if not org.active:
           return None

       if not org.subscription_active:
           return None

       return org

   finally:
       db.close()