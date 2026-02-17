from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.sql import func
from tenancy.models import Base


class FinancialPolicy(Base):
   __tablename__ = "financial_policies"

   id = Column(String, primary_key=True)
   tenant_id = Column(String, nullable=False)

   version = Column(Integer, nullable=False)

   max_transaction_amount = Column(Float, nullable=False)
   max_daily_amount = Column(Float, nullable=False)
   max_risk_score = Column(Float, nullable=False)

   blocked_categories = Column(String, nullable=False)  # JSON string

   created_at = Column(DateTime(timezone=True), server_default=func.now())