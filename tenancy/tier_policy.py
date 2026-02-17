from typing import Dict, Any, Optional
from dataclasses import dataclass


# ============================================================
# TIER LIMITS & CAPABILITIES
# ============================================================

TIER_LIMITS: Dict[str, Dict[str, Optional[int]]] = {
   "starter": {
       "monthly_decisions": 1000,
       "rate_limit_per_minute": 30,
   },
   "pro": {
       "monthly_decisions": 10000,
       "rate_limit_per_minute": 120,
   },
   "enterprise": {
       "monthly_decisions": None,  # unlimited
       "rate_limit_per_minute": 500,
   },
}


TIER_CAPABILITIES: Dict[str, Dict[str, bool]] = {
   "starter": {
       "risk_scoring": False,
       "explainability": False,
       "audit_logging": False,
   },
   "pro": {
       "risk_scoring": True,
       "explainability": False,
       "audit_logging": True,
   },
   "enterprise": {
       "risk_scoring": True,
       "explainability": True,
       "audit_logging": True,
   },
}


# ============================================================
# PRICING MODEL
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

   total = round(total, -2)

   return {
       "base_price": base,
       "final_price": total,
       "applied_multipliers": multipliers,
   }


# ============================================================
# ENFORCEMENT HELPERS
# ============================================================

def get_tier_limits(tier: str) -> Dict[str, Optional[int]]:
   if tier not in TIER_LIMITS:
       raise ValueError(f"Invalid tier: {tier}")
   return TIER_LIMITS[tier]


def get_tier_capabilities(tier: str) -> Dict[str, bool]:
   if tier not in TIER_CAPABILITIES:
       raise ValueError(f"Invalid tier: {tier}")
   return TIER_CAPABILITIES[tier]


def tier_allows_feature(tier: str, feature: str) -> bool:
   capabilities = get_tier_capabilities(tier)
   return capabilities.get(feature, False)