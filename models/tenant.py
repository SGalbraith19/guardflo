import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class Tenant(Base):
   __tablename__ = "tenants"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   name = Column(String, nullable=False)

   stripe_customer_id = Column(String, nullable=True)

   tier = Column(String, nullable=False, default="starter")

   monthly_quota = Column(Integer, nullable=False, default=1000)

   active = Column(Boolean, default=True)

   created_at = Column(DateTime, default=datetime.utcnow)