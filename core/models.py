from sqlalchemy import (
   Column,
   Integer,
   String,
   DateTime,
   Text,
   ForeignKey,
   Float,
   Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# ============================
# AI EVENT (root object)
# ============================

class AIEvent(Base):
   __tablename__ = "ai_events"

   id = Column(Integer, primary_key=True, index=True)
   event_type = Column(String, nullable=False)
   payload = Column(Text, nullable=False)
   received_at = Column(DateTime, default=datetime.utcnow)

   explanations = relationship("AIExplanation", back_populates="event")
   risks = relationship("AIRisk", back_populates="event")
   recommendations = relationship("AIRecommendation", back_populates="event")
   approvals = relationship("AIApproval", back_populates="event")


# ============================
# AI EXPLANATION
# ============================

class AIExplanation(Base):
   __tablename__ = "ai_explanations"

   id = Column(Integer, primary_key=True)
   event_id = Column(Integer, ForeignKey("ai_events.id"), nullable=False)

   summary = Column(Text)
   reasoning = Column(Text)

   event = relationship("AIEvent", back_populates="explanations")


# ============================
# AI RISK
# ============================

class AIRisk(Base):
   __tablename__ = "ai_risks"

   id = Column(Integer, primary_key=True)
   event_id = Column(Integer, ForeignKey("ai_events.id"), nullable=False)

   risk_score = Column(Float)
   risk_level = Column(String)

   event = relationship("AIEvent", back_populates="risks")


# ============================
# AI RECOMMENDATION
# ============================

class AIRecommendation(Base):
   __tablename__ = "ai_recommendations"

   id = Column(Integer, primary_key=True)
   event_id = Column(Integer, ForeignKey("ai_events.id"), nullable=False)

   recommendation = Column(Text)
   confidence = Column(Float)

   event = relationship("AIEvent", back_populates="recommendations")


# ============================
# AI APPROVAL
# ============================

class AIApproval(Base):
   __tablename__ = "ai_approvals"

   id = Column(Integer, primary_key=True)
   event_id = Column(Integer, ForeignKey("ai_events.id"), nullable=False)

   approved = Column(Boolean)
   approver = Column(String)
   approved_at = Column(DateTime, default=datetime.utcnow)

   event = relationship("AIEvent", back_populates="approvals")