# ai_service/main.py
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import json
import os
from datetime import datetime

# === AI interpretation modules (READ-ONLY) ===
from explainer import explain_event
from llm_explainer import llm_explain_event
from risk_engine import detect_risks
from recommendation_engine import generate_recommendations
from storage import store_approval
from report_generator import generate_operational_summary

# === AI-owned persistence layer ===
from storage import (
   init_db,
   store_event,
   store_explanation,
   store_risks,
   store_recommendations,
)

# ======================================================
# App setup
# ======================================================
app = FastAPI(title="AI Interpretation Service")

# ======================================================
# Configuration
# ======================================================
WEBHOOK_SECRET = os.getenv("AI_WEBHOOK_SECRET", "dev-secret")
USE_LLM = os.getenv("USE_LLM_EXPLAINER", "false").lower() == "true"

# ======================================================
# Initialise AI-owned database
# ======================================================
init_db()

# ======================================================
# Security: webhook signature verification
# ======================================================
def verify_signature(payload: bytes, signature: str) -> bool:
   expected = hmac.new(
       WEBHOOK_SECRET.encode(),
       payload,
       hashlib.sha256,
   ).hexdigest()
   return hmac.compare_digest(expected, signature)


# ======================================================
# Health check
# ======================================================
@app.get("/health")
def health_check():
   return {
       "status": "ok",
       "llm_enabled": USE_LLM,
   }


# ======================================================
# Webhook ingestion (READ-ONLY, NON-AUTHORITATIVE)
# ======================================================
@app.post("/events")
async def receive_event(request: Request):
   raw_body = await request.body()
   signature = request.headers.get("X-Signature")

   if not signature:
       raise HTTPException(status_code=401, detail="Missing signature")

   if not verify_signature(raw_body, signature):
       raise HTTPException(status_code=403, detail="Invalid signature")

   try:
       event = json.loads(raw_body.decode())
   except Exception:
       raise HTTPException(status_code=400, detail="Invalid JSON payload")

   # AI-only metadata (does NOT go back to engine)
   event["_received_at"] = datetime.utcnow().isoformat()

   # ==================================================
   # 1. Persist immutable event
   # ==================================================
   event_id = store_event(event)

   # ==================================================
   # 2. Generate explanation (deterministic or LLM)
   # ==================================================
   if USE_LLM:
       explanation = llm_explain_event(event)
   else:
       explanation = explain_event(event)

   store_explanation(event_id, explanation)

   # ==================================================
   # 3. Detect risks (NON-BINDING)
   # ==================================================
   risks = detect_risks([event])
   store_risks(risks)

   # ==================================================
   # 4. Generate NON-BINDING recommendations
   # ==================================================
   recommendations = generate_recommendations([event], risks)
   store_recommendations(recommendations)

   return {
       "status": "accepted",
       "explanation_confidence": explanation.get("confidence"),
       "risk_count": len(risks),
   }
@app.post("/approvals")
async def record_approval(payload: dict):
   """
   Record approval or rejection of an AI recommendation.
   This endpoint does NOT execute anything.
   """

   try:
       store_approval(
           recommendation_id=payload["recommendation_id"],
           decision=payload["decision"],
           approved_by=payload["approved_by"],
           approval_context=payload.get("approval_context"),
       )
   except KeyError as e:
       raise HTTPException(status_code=400, detail=f"Missing field: {e}")
   except ValueError as e:
       raise HTTPException(status_code=400, detail=str(e))

   return {
       "status": "recorded",
       "recommendation_id": payload["recommendation_id"],
       "decision": payload["decision"],
   }
@app.get("/reports/operational-summary")
def get_operational_summary():
   """
   Read-only operational summary report.
   Safe for auditors, operators, and regulators.
   """
   return generate_operational_summary()

@app.get("/approval-ui", response_class=HTMLResponse)
def serve_approval_ui():
   html_path = Path(__file__).parent / "approval_ui" / "index.html"
   return html_path.read_text()