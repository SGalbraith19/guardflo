import json
import hashlib

from core.policy_runtime import evaluate
from core.graph_db import link_entities, compute_graph_risk


def run_financial_decision(request, organisation, policy):
   """
   Deterministic financial decision engine.

   No AI
   No randomness
   No external calls
   """

   # Load policy definition
   with open("policies/high_risk.json") as f:
       policy = json.load(f)

   # Convert request into dictionary safely
   if isinstance(request, dict):
       request_data = request
   else:
       request_data = request.dict()

   # Extract graph entities
   card = request_data.get("card_token")
   email = request_data.get("email")
   ip = request_data.get("ip_address")

   # Build entity graph relationships
   if card and email:
       link_entities(card, email)

   if card and ip:
       link_entities(card, ip)

   # Evaluate policy rules
   violations = evaluate(policy, request_data)

   # Graph risk score
   graph_risk = compute_graph_risk(card) if card else 0

   # Risk score calculation
   risk_score = (len(violations) * 50) + (graph_risk * 10)

   approved = len(violations) == 0

   # Decision trace
   decision_trace = []

   if graph_risk > 5:
       decision_trace.append("rule:graph_high_risk")

   for v in violations:
       decision_trace.append(f"rule:{v}")

   # Explanation
   explanation = ", ".join(violations) if violations else "no violations"

   # Deterministic request hash
   request_hash = hashlib.sha256(
       json.dumps(
           request_data,
           separators=(",", ":"),
           sort_keys=True,
           default=str
       ).encode()
   ).hexdigest()

   return {
       "approved": approved,
       "risk_score": risk_score,
       "violations": violations,
       "explanation": explanation,
       "trace": decision_trace,
       "request_hash": request_hash,
       "graph_risk": graph_risk
   }