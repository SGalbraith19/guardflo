import hashlib
import json
import uuid

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from tenancy.models import Base


class FinancialLedger(Base):
   __tablename__ = "financial_ledger"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   tenant_id = Column(String, nullable=False)

   policy_version = Column(String, nullable=False)
   request_hash = Column(String, nullable=False)
   decision = Column(String, nullable=False)
   signature = Column(String, nullable=False)

   previous_hash = Column(String, nullable=True)
   entry_hash = Column(String, nullable=False)

   created_at = Column(DateTime(timezone=True), server_default=func.now())