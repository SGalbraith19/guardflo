# ai_service/storage.py

import sqlite3
import json
from datetime import datetime
from typing import Dict, List

DB_PATH = "ai_data.db"


# ======================================================
# Database initialisation
# ======================================================
def init_db():
   conn = sqlite3.connect(DB_PATH)
   cur = conn.cursor()

   # Raw immutable events received by AI
   cur.execute("""
       CREATE TABLE IF NOT EXISTS ai_events (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           event_type TEXT NOT NULL,
           payload TEXT NOT NULL,
           received_at TEXT NOT NULL
       )
   """)

   # AI explanations (derived, non-authoritative)
   cur.execute("""
       CREATE TABLE IF NOT EXISTS ai_explanations (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           event_id INTEGER NOT NULL,
           explanation TEXT NOT NULL,
           confidence REAL,
           model TEXT,
           created_at TEXT NOT NULL,
           FOREIGN KEY(event_id) REFERENCES ai_events(id)
       )
   """)

   # Detected risks
   cur.execute("""
       CREATE TABLE IF NOT EXISTS ai_risks (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           risk_type TEXT NOT NULL,
           data TEXT NOT NULL,
           detected_at TEXT NOT NULL
       )
   """)

   # Non-binding recommendations
   cur.execute("""
       CREATE TABLE IF NOT EXISTS ai_recommendations (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           recommendation TEXT NOT NULL,
           created_at TEXT NOT NULL
       )
   """)

   conn.commit()
   conn.close()


# ======================================================
# Persistence helpers
# ======================================================
def store_event(event: Dict) -> int:
   conn = sqlite3.connect(DB_PATH)
   cur = conn.cursor()

   cur.execute(
       """
       INSERT INTO ai_events (event_type, payload, received_at)
       VALUES (?, ?, ?)
       """,
       (
           event.get("event_type"),
           json.dumps(event.get("payload")),
           event.get("_received_at"),
       )
   )

   event_id = cur.lastrowid
   conn.commit()
   conn.close()
   return event_id


def store_explanation(event_id: int, explanation: Dict):
   conn = sqlite3.connect(DB_PATH)
   cur = conn.cursor()

   cur.execute(
       """
       INSERT INTO ai_explanations (
           event_id, explanation, confidence, model, created_at
       )
       VALUES (?, ?, ?, ?, ?)
       """,
       (
           event_id,
           json.dumps(explanation),
           explanation.get("confidence"),
           explanation.get("model"),
           datetime.utcnow().isoformat(),
       )
   )

   conn.commit()
   conn.close()


def store_risks(risks: List[Dict]):
   conn = sqlite3.connect(DB_PATH)
   cur = conn.cursor()

   for risk in risks:
       cur.execute(
           """
           INSERT INTO ai_risks (risk_type, data, detected_at)
           VALUES (?, ?, ?)
           """,
           (
               risk.get("type"),
               json.dumps(risk),
               datetime.utcnow().isoformat(),
           )
       )

   conn.commit()
   conn.close()


def store_recommendations(recommendations: List[Dict]):
   conn = sqlite3.connect(DB_PATH)
   cur = conn.cursor()

   for rec in recommendations:
       cur.execute(
           """
           INSERT INTO ai_recommendations (recommendation, created_at)
           VALUES (?, ?)
           """,
           (
               json.dumps(rec),
               datetime.utcnow().isoformat(),
           )
       )
     # Human / system approvals of AI recommendations
   cur.execute("""
       CREATE TABLE IF NOT EXISTS ai_approvals (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           recommendation_id TEXT NOT NULL,
           decision TEXT NOT NULL,  -- approved | rejected
           approved_by TEXT NOT NULL,
           approval_context TEXT,
           approved_at TEXT NOT NULL
       )
   """) 

   conn.commit()
   conn.close()

def store_approval(
   recommendation_id: str,
   decision: str,
   approved_by: str,
   approval_context: str = None,
):
   """
   Persist a human or system approval/rejection.
   This does NOT trigger any execution.
   """

   if decision not in ("approved", "rejected"):
       raise ValueError("decision must be 'approved' or 'rejected'")

   conn = sqlite3.connect(DB_PATH)
   cur = conn.cursor()

   cur.execute(
       """
       INSERT INTO ai_approvals (
           recommendation_id,
           decision,
           approved_by,
           approval_context,
           approved_at
       )
       VALUES (?, ?, ?, ?, ?)
       """,
       (
           recommendation_id,
           decision,
           approved_by,
           approval_context,
           datetime.utcnow().isoformat(),
       )
   )

   conn.commit()
   conn.close()
