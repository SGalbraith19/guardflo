from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base


class APIKey(Base):
   __tablename__ = "api_keys"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
   key_hash = Column(String, nullable=False)
   active = Column(Boolean, default=True)
   created_at = Column(DateTime, default=datetime.utcnow)