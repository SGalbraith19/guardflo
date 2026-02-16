from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FinancialDecisionRequest(BaseModel):
   tenant_id: str = Field(..., description="Tenant making the request")
   amount: float = Field(..., gt=0)
   currency: str = Field(..., min_length=3, max_length=3)
   vendor_id: str
   vendor_risk_score: float = Field(ge=0, le=100)
   duplicate_flag: bool
   approval_chain_depth: int = Field(..., ge=0)
   fan_out: int = Field(..., ge=1)
   created_at: Optional[datetime] = None


class FinancialDecisionResponse(BaseModel):
   approved: bool
   risk_score: Optional[float] = None
   violations: Optional[List[str]] = None
   explanation: Optional[str] = None
   decision_id: str
   timestamp: datetime