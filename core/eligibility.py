# support_ai/eligibility.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SupportEligibility:
   eligible: bool
   reason: str
   enforced_org_size: Optional[str] = None


def evaluate_support_eligibility(
   declared_org_size: str,
   production_instances: Optional[int] = None,
   critical_path: Optional[bool] = None,
   audit_exposure: Optional[bool] = None,
) -> SupportEligibility:
   """
   Determines whether an organisation is eligible for a given support tier.

   This function enforces eligibility, not pricing.
   """

   # Large org enforcement
   if (
       production_instances and production_instances >= 3
       or critical_path is True
       or audit_exposure is True
   ):
       if declared_org_size != "large":
           return SupportEligibility(
               eligible=False,
               enforced_org_size="large",
               reason=(
                   "Declared organisation size is inconsistent with operational "
                   "signals indicating large-organisation dependency."
               ),
           )

   # Medium org enforcement
   if production_instances and production_instances >= 1:
       if declared_org_size == "small":
           return SupportEligibility(
               eligible=False,
               enforced_org_size="medium",
               reason=(
                   "Declared organisation size is inconsistent with "
                   "production usage signals."
               ),
           )

   return SupportEligibility(
       eligible=True,
       enforced_org_size=declared_org_size,
       reason="Eligibility signals are consistent with declared organisation size.",
   )