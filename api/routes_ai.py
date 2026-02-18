from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path

from core.ai.ai_pipeline import (
   process_event,
   record_approval,
   get_operational_summary,
)

router = APIRouter()



# --- Webhook Ingestion ---
@router.post("/ai/events")
async def receive_event(request: Request):
   raw_body = await request.body()
   signature = request.headers.get("X-Signature")

   try:
       return process_event(raw_body, signature)
   except ValueError as e:
       if "Missing signature" in str(e):
           raise HTTPException(status_code=401, detail=str(e))
       if "Invalid signature" in str(e):
           raise HTTPException(status_code=403, detail=str(e))
       raise HTTPException(status_code=400, detail=str(e))


# --- Approval Recording ---
@router.post("/ai/approvals")
async def approval_endpoint(payload: dict):
   try:
       return record_approval(payload)
   except ValueError as e:
       raise HTTPException(status_code=400, detail=str(e))


# --- Reports ---
@router.get("/ai/reports/operational-summary")
def operational_summary():
   return get_operational_summary()


# --- Approval UI ---
@router.get("/ai/approval-ui", response_class=HTMLResponse)
def serve_approval_ui():
   html_path = (
       Path(__file__).parent.parent / "ui" / "approval_ui" / "index.html"
   )
   return html_path.read_text()