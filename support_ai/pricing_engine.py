# support_ai/pricing_engine.py

from dataclasses import dataclass


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


def calculate_pricing(input: PricingInput) -> dict:
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