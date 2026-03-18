from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import secrets

from uuid import UUID


class FinancialDecisionRequest(BaseModel):
   tenant_id: UUID = Field(..., description="Tenant making the request")
   policy_version: int
   amount: float = Field(..., gt=0)
   currency: str = Field(..., min_length=3, max_length=3)
   vendor_id: str
   vendor_risk_score: float = Field(ge=0, le=100)
   duplicate_flag: bool
   approval_chain_depth: int = Field(..., ge=0)
   fan_out: int = Field(..., ge=1)
   created_at: Optional[datetime] = None
   nonce: int = 0
   category: Optional[str] = None
   actor_type: Optional[str] = None
   agent_id: Optional[str] = None

   nonce: str = Field(default_factory=lambda: secrets.token_hex(16))


class FinancialDecisionResponse(BaseModel):
   decision_id: str
   tenant_id: str
   policy_version: int
   engine_version: str
   timestamp: str
   approved: bool
   risk_score: float
   violations: list
   explanation: str
   signature: str