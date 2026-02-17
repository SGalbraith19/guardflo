from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from tenancy.models import Base


class PolicyRegistry(Base):
   __tablename__ = "policy_registry"

   version = Column(String, primary_key=True)
   policy_hash = Column(String, nullable=False)
   created_at = Column(DateTime(timezone=True), server_default=func.now())