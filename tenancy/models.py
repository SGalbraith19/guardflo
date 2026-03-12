from datetime import datetime
import uuid

from sqlalchemy import (
   Column,
   Integer,
   String,
   Boolean,
   Float,
   DateTime,
   ForeignKey,
   JSON,
   Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


# =========================================================
# ORGANISATION (TENANT ROOT)
# =========================================================

class Organisation(Base):
   __tablename__ = "organisations"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   org_name = Column(String, unique=True, nullable=False)

   # Subscription
   tier = Column(String, nullable=False, default="free")
   subscription_active = Column(Boolean, default=True, nullable=False)

   # API Security
   api_key = Column(String, unique=True, nullable=False, index=True)

   # Stripe
   stripe_customer_id = Column(String, nullable=True)
   stripe_subscription_id = Column(String, nullable=True)

   # Metadata
   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

   monthly_decisions = Column(Integer, default=0)
   monthly_quota = Column(Integer, default=1000)

   # Relationships
   decisions = relationship("FinancialDecision", back_populates="organisation")
   quotes = relationship("Quote", back_populates="organisation")
   usage_records = relationship("UsageRecord", back_populates="organisation")

   
# =========================================================
# FINANCIAL DECISIONS (LEDGER SOURCE)
# =========================================================

class FinancialDecision(Base):
   __tablename__ = "financial_decisions"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   organisation_id = Column(
       UUID(as_uuid=True),
       ForeignKey("organisations.id"),
       nullable=False,
       index=True,
   )

   approved = Column(Boolean, nullable=False)
   risk_score = Column(Float, nullable=False)
   violations = Column(JSON, nullable=False)
   explanation = Column(String, nullable=False)

   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

   organisation = relationship("Organisation", back_populates="decisions")


# =========================================================
# QUOTES
# =========================================================

class Quote(Base):
   __tablename__ = "quotes"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   organisation_id = Column(
       UUID(as_uuid=True),
       ForeignKey("organisations.id"),
       nullable=False,
       index=True,
   )

   tier = Column(String, nullable=False)

   base_price = Column(Float, nullable=False)
   final_price = Column(Float, nullable=False)

   production = Column(Boolean, default=False)
   sla_24_7 = Column(Boolean, default=False)

   applied_multipliers = Column(JSON, nullable=False)
   signature = Column(String, nullable=False)

   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

   organisation = relationship("Organisation", back_populates="quotes")


# =========================================================
# USAGE METERING (CONCURRENCY SAFE)
# =========================================================

class UsageRecord(Base):
   __tablename__ = "usage_records"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   organisation_id = Column(
       UUID(as_uuid=True),
       ForeignKey("organisations.id"),
       nullable=False,
       index=True,
   )

   endpoint = Column(String, nullable=False)
   request_hash = Column(String, nullable=False)

   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

   organisation = relationship("Organisation", back_populates="usage_records")