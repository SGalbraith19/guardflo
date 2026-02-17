from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from tenancy.models import Base


class FinancialDecision(Base):
   __tablename__ = "financial_decisions"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   tenant_id = Column(String, nullable=False)
   request_hash = Column(String, nullable=False)
   decision = Column(String, nullable=False)
   policy_version = Column(String, nullable=False)
   signature = Column(String, nullable=False)
   created_at = Column(DateTime(timezone=True), server_default=func.now())