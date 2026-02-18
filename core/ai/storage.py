from sqlalchemy.orm import Session
from datetime import datetime
import json

from database import SessionLocal
from models import (
   AIEvent,
   AIExplanation,
   AIRisk,
   AIRecommendation,
   AIApproval,
)


def store_event(event: dict) -> int:
   db: Session = SessionLocal()
   try:
       db_event = AIEvent(
           event_type=event.get("event_type"),
           payload=json.dumps(event.get("payload")),
           received_at=event.get("received_at") or datetime.utcnow().isoformat(),
       )
       db.add(db_event)
       db.commit()
       db.refresh(db_event)
       return db_event.id
   finally:
       db.close()


def store_explanation(event_id: int, explanation: dict):
   db: Session = SessionLocal()
   try:
       db_exp = AIExplanation(
           event_id=event_id,
           explanation=json.dumps(explanation),
           confidence=explanation.get("confidence"),
           model=explanation.get("model"),
           created_at=datetime.utcnow().isoformat(),
       )
       db.add(db_exp)
       db.commit()
   finally:
       db.close()


def store_risks(risks: list[dict]):
   db: Session = SessionLocal()
   try:
       for risk in risks:
           db_risk = AIRisk(
               risk_type=risk.get("type"),
               data=json.dumps(risk),
               detected_at=datetime.utcnow().isoformat(),
           )
           db.add(db_risk)
       db.commit()
   finally:
       db.close()


def store_recommendations(recommendations: list[dict]):
   db: Session = SessionLocal()
   try:
       for rec in recommendations:
           db_rec = AIRecommendation(
               recommendation=json.dumps(rec),
               created_at=datetime.utcnow().isoformat(),
           )
           db.add(db_rec)
       db.commit()
   finally:
       db.close()


def store_approval(
   recommendation_id: str,
   decision: str,
   approved_by: str,
   approval_context: str | None = None,
):
   if decision not in ["approved", "rejected"]:
       raise ValueError("decision must be 'approved' or 'rejected'")

   db: Session = SessionLocal()
   try:
       db_approval = AIApproval(
           recommendation_id=recommendation_id,
           decision=decision,
           approved_by=approved_by,
           approval_context=approval_context,
           approved_at=datetime.utcnow().isoformat(),
       )
       db.add(db_approval)
       db.commit()
   finally:
       db.close()