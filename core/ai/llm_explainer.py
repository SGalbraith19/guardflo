# ai_service/llm_explainer.py

import os
import json
from typing import Dict

# Placeholder for LLM call
# You can later replace this with OpenAI, Azure, local model, etc.

def explain_event(event: Dict) -> Dict:
   """
   Produce a natural-language explanation for an immutable domain event.
   This function MUST be read-only and non-authoritative.
   """

   event_type = event.get("event_type")
   payload = event.get("payload", {})

   # Deterministic fallback explanation
   explanation = (
       f"Event '{event_type}' occurred with payload: "
       f"{json.dumps(payload, indent=2)}"
   )

   return {
       "summary": f"AI interpretation of {event_type}",
       "confidence": 0.85,
       "explanation": explanation,
       "model": "llm-placeholder",
   }