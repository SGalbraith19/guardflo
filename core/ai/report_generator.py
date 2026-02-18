from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from core.models import (
   AIEvent,
   AIExplanation,
   AIRisk,
   AIRecommendation,
   AIApproval,
)


def generate_operational_summary(limit: int = 50) -> dict:
   db: Session = SessionLocal()

   try:
       # ---- Fetch recent events ----
       events = (
           db.query(AIEvent)
           .order_by(AIEvent.received_at.desc())
           .limit(limit)
           .all()
       )

       # ---- Fetch explanations ----
       explanations = {
           e.event_id: e.explanation
           for e in db.query(AIExplanation).all()
       }

       # ---- Fetch risks ----
       risks = [
           {
               "risk_type": r.risk_type,
               "details": r.data,
               "detected_at": r.detected_at,
           }
           for r in db.query(AIRisk)
           .order_by(AIRisk.detected_at.desc())
           .all()
       ]

       # ---- Fetch recommendations ----
       recommendations = [
           {
               "recommendation": r.recommendation,
               "created_at": r.created_at,
           }
           for r in db.query(AIRecommendation)
           .order_by(AIRecommendation.created_at.desc())
           .all()
       ]

       # ---- Fetch approvals ----
       approvals = [
           {
               "recommendation_id": a.recommendation_id,
               "decision": a.decision,
               "approved_by": a.approved_by,
               "approval_context": a.approval_context,
               "approved_at": a.approved_at,
           }
           for a in db.query(AIApproval)
           .order_by(AIApproval.approved_at.desc())
           .all()
       ]

       # ---- Assemble report ----
       report_events = [
           {
               "event_id": e.id,
               "event_type": e.event_type,
               "payload": e.payload,
               "received_at": e.received_at,
               "ai_explanation": explanations.get(e.id),
           }
           for e in events
       ]

       return {
           "report_type": "Operational Summary",
           "generated_at": datetime.utcnow().isoformat(),
           "event_count": len(report_events),
           "events": report_events,
           "risks_detected": risks,
           "recommendations": recommendations,
           "approvals": approvals,
       }

   finally:
       db.close()