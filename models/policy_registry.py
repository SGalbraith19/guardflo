from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from tenancy.models import Base


class PolicyRegistry(Base):
   __tablename__ = "policy_registry"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   version = Column(String, nullable=False, unique=True)
   definition = Column(JSON, nullable=False)
   is_active = Column(Boolean, default=False, nullable=False)
   is_locked = Column(Boolean, default=False, nullable=False)
   created_at = Column(DateTime(timezone=True), server_default=func.now())