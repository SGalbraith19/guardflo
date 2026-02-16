from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Organisation(Base):
   __tablename__ = "organisations"

   id = Column(Integer, primary_key=True)
   name = Column(String, unique=True)
   tier = Column(String)
   api_key = Column(String, unique=True)
   subscription_active = Column(Boolean, default=False)


class Quote(Base):
   __tablename__ = "quotes"

   id = Column(Integer, primary_key=True)
   organisation = Column(String)
   tier = Column(String)

   base_price = Column(Float)
   final_price = Column(Float)

   production = Column(Boolean)
   sla_24_7 = Column(Boolean)

   applied_multipliers = Column(JSON)

   signature = Column(String)

   created_at = Column(DateTime, default=datetime.utcnow)

class FinancialDecision(Base):
   __tablename__ = "financial_decisions"

   id = Column(String, primary_key=True)
   organisation = Column(String)
   approved = Column(Boolean)
   risk_score = Column(Float)
   violations = Column(JSON)
   explanation = Column(String)
   created_at = Column(DateTime, default=datetime.utcnow)

class UsageRecord(Base):
   __tablename__ = "usage_records"

   id = Column(Integer, primary_key=True)
   organisation = Column(String)
   month = Column  # e.g. "2026-02"
   decision_count = Column(Integer, default=0)