from sqlalchemy import (
   Column,
   String,
   Integer,
   Float,
   Boolean,
   DateTime,
   JSON,
   ForeignKey,
)
from datetime import datetime
import uuid

# 🔥 IMPORTANT — import Base from database
from database import Base


# =====================================================
# TENANT / ORGANISATION
# =====================================================

class Organisation(Base):
   __tablename__ = "organisations"

   id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
   org_name = Column(String, unique=True, nullable=False)

   # Subscription & Tier
   tier = Column(String, nullable=False, default="free")  # free | small | medium | large
   subscription_active = Column(Boolean, default=False)

   # API Security
   api_key = Column(String, unique=True, nullable=False)

   # Stripe
   stripe_customer_id = Column(String, nullable=True)
   stripe_subscription_id = Column(String, nullable=True)

   # Metadata
   created_at = Column(DateTime, default=datetime.utcnow)
   active = Column(Boolean, default=True)


# =====================================================
# FINANCIAL DECISIONS
# =====================================================

class FinancialDecision(Base):
   __tablename__ = "financial_decisions"

   id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
   id = Column(String, ForeignKey("organisations.id"), nullable=False)

   approved = Column(Boolean)
   risk_score = Column(Float)
   violations = Column(JSON)
   explanation = Column(String)

   created_at = Column(DateTime, default=datetime.utcnow)


# =====================================================
# QUOTES
# =====================================================

class Quote(Base):
   __tablename__ = "quotes"

   id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
   id = Column(String, ForeignKey("organisations.id"), nullable=False)

   tier = Column(String)

   base_price = Column(Float)
   final_price = Column(Float)

   production = Column(Boolean)
   sla_24_7 = Column(Boolean)

   applied_multipliers = Column(JSON)
   signature = Column(String)

   created_at = Column(DateTime, default=datetime.utcnow)


# =====================================================
# USAGE METERING
# =====================================================

class UsageRecord(Base):
   __tablename__ = "usage_records"

   id = Column(Integer, primary_key=True, autoincrement=True)
   id = Column(String, ForeignKey("organisations.id"), nullable=False)

   month = Column(String, nullable=False)  # e.g. "2026-02"
   decision_count = Column(Integer, default=0)

   created_at = Column(DateTime, default=datetime.utcnow)