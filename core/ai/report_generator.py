# ai_service/report_generator.py

import sqlite3
import json
from datetime import datetime

DB_PATH = "ai_data.db"


def generate_operational_summary(limit: int = 50) -> dict:
   """
   Generate a human-readable operational summary report
   based entirely on AI-owned, immutable records.
   """

   conn = sqlite3.connect(DB_PATH)
   cur = conn.cursor()

   # --- Fetch recent events ---
   cur.execute("""
       SELECT id, event_type, payload, received_at
       FROM ai_events
       ORDER BY received_at DESC
       LIMIT ?
   """, (limit,))
   events = cur.fetchall()

   # --- Fetch explanations ---
   cur.execute("""
       SELECT event_id, explanation
       FROM ai_explanations
   """)
   explanations = {
       row[0]: json.loads(row[1])
       for row in cur.fetchall()
   }

   # --- Fetch risks ---
   cur.execute("""
       SELECT risk_type, data, detected_at
       FROM ai_risks
       ORDER BY detected_at DESC
   """)
   risks = [
       {
           "risk_type": r[0],
           "details": json.loads(r[1]),
           "detected_at": r[2],
       }
       for r in cur.fetchall()
   ]

   # --- Fetch recommendations ---
   cur.execute("""
       SELECT recommendation, created_at
       FROM ai_recommendations
       ORDER BY created_at DESC
   """)
   recommendations = [
       {
           "recommendation": json.loads(r[0]),
           "created_at": r[1],
       }
       for r in cur.fetchall()
   ]

   # --- Fetch approvals ---
   cur.execute("""
       SELECT recommendation_id, decision, approved_by, approval_context, approved_at
       FROM ai_approvals
       ORDER BY approved_at DESC
   """)
   approvals = [
       {
           "recommendation_id": r[0],
           "decision": r[1],
           "approved_by": r[2],
           "approval_context": r[3],
           "approved_at": r[4],
       }
       for r in cur.fetchall()
   ]

   conn.close()

   # --- Assemble report ---
   report_events = []
   for e in events:
       event_id = e[0]
       report_events.append({
           "event_id": event_id,
           "event_type": e[1],
           "payload": json.loads(e[2]),
           "received_at": e[3],
           "ai_explanation": explanations.get(event_id),
       })

   return {
       "report_type": "Operational Summary",
       "generated_at": datetime.utcnow().isoformat(),
       "event_count": len(report_events),
       "events": report_events,
       "risks_detected": risks,
       "recommendations": recommendations,
       "approvals": approvals,
   }