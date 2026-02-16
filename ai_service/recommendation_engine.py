# ai_service/recommendation_engine.py

import uuid
from datetime import datetime


def generate_recommendations(events: list, risks: list) -> list:
   """
   Generate non-binding, human-reviewable action proposals.
   This function NEVER executes changes.
   """

   recommendations = []

   for risk in risks:
       if risk["type"] == "capacity_pressure":
           recommendation = {
               "recommendation_id": str(uuid.uuid4()),
               "type": "proposed_action",
               "target": {
                   "entity": "site",
                   "id": risk.get("site"),
               },
               "proposal": {
                   "action": "review_capacity_plan",
                   "parameters": {
                       "date": risk.get("date"),
                   },
               },
               "reasoning": {
                   "risk_type": risk["type"],
                   "explanation": risk["message"],
                   "confidence": 0.8,
               },
               "constraints": {
                   "requires_human_approval": True,
                   "auto_execution_allowed": False,
               },
               "created_at": datetime.utcnow().isoformat(),
           }

           recommendations.append(recommendation)

   return recommendations