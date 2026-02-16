from pydantic import BaseModel, Field
from typing import Literal, Optional


class SupportQuery(BaseModel):
   """
   Structured input for support queries.
   Intentionally restrictive to prevent pricing manipulation.
   """

   question: str = Field(..., min_length=5, max_length=2000)

   request_type: Literal[
       "general",
       "pricing",
       "support_scope",
       "contract"
   ]

   # --- Pricing & eligibility signals (required for pricing) ---

   org_size: Optional[Literal["small", "medium", "large"]] = None

   production_instances: Optional[int] = Field(
       None, ge=0, description="Number of production deployments"
   )

   critical_path: Optional[bool] = Field(
       None, description="Whether the system is on a critical execution path"
   )

   audit_exposure: Optional[bool] = Field(
       None, description="Whether failures would be audit-relevant"
   )