import os
import hmac
import hashlib
import json
from datetime import datetime

from core.ai.llm_explainer import explain_event
from core.risk_engine import detect_risks
from core.ai.recommendation_engine import generate_recommendations
from core.ai.report_generator import generate_operational_summary
from core.ai.storage import (
   init_db,
   store_event,
   store_explanation,
   store_risks,
   store_recommendations,
   store_approval,
)

# --- Configuration ---
WEBHOOK_SECRET = os.getenv("AI_WEBHOOK_SECRET", "dev-secret")
USE_LLM = os.getenv("USE_LLM_EXPLAINER", "false").lower() == "true"

# Initialise AI-owned tables (now using main DB)
init_db()


# --- Security ---
def verify_signature(payload: bytes, signature: str) -> bool:
   expected = hmac.new(
       WEBHOOK_SECRET.encode(),
       payload,
       hashlib.sha256,
   ).hexdigest()

   return hmac.compare_digest(expected, signature)


# --- Core Processing ---
def process_event(raw_body: bytes, signature: str):
   if not signature:
       raise ValueError("Missing signature")

   if not verify_signature(raw_body, signature):
       raise ValueError("Invalid signature")

   try:
       event = json.loads(raw_body.decode())
   except Exception:
       raise ValueError("Invalid JSON payload")

   # AI-only metadata
   event["_received_at"] = datetime.utcnow().isoformat()

   # 1. Persist immutable event
   event_id = store_event(event)

   # 2. Generate explanation
   if USE_LLM:
       explanation = explain_event(event)
   else:
       explanation = explain_event(event)

   store_explanation(event_id, explanation)

   # 3. Detect risks (non-binding)
   risks = detect_risks([event])
   store_risks(risks)

   # 4. Generate recommendations (non-binding)
   recommendations = generate_recommendations([event], risks)
   store_recommendations(recommendations)

   return {
       "status": "accepted",
       "explanation_confidence": explanation.get("confidence"),
       "risk_count": len(risks),
   }


def record_approval(payload: dict):
   try:
       store_approval(
           recommendation_id=payload["recommendation_id"],
           decision=payload["decision"],
           approved_by=payload["approved_by"],
           approval_context=payload.get("approval_context"),
       )
   except KeyError as e:
       raise ValueError(f"Missing field: {e}")
   except Exception as e:
       raise ValueError(str(e))

   return {
       "status": "recorded",
       "recommendation_id": payload["recommendation_id"],
       "decision": payload["decision"],
   }


def get_operational_summary():
   return generate_operational_summary()