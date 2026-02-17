# ai_service/risk_engine.py

from collections import defaultdict
from datetime import datetime, timedelta


def detect_risks(events: list) -> list:
   """
   Analyze recent immutable events and surface early warning signals.
   This function is read-only and produces non-authoritative insights.
   """

   risks = []

   # Filter to last 24 hours of events
   recent_events = []
   for e in events:
       received_at = e.get("_received_at")
       if not received_at:
           continue

       try:
           ts = datetime.fromisoformat(received_at)
       except ValueError:
           continue

       if ts > datetime.utcnow() - timedelta(hours=24):
           recent_events.append(e)

   # Track repeated capacity hits
   capacity_hits = defaultdict(int)

   for e in recent_events:
       if e.get("event_type") == "capacity.limit_reached":
           payload = e.get("payload", {})
           key = (
               payload.get("site"),
               payload.get("date"),
           )
           capacity_hits[key] += 1

   # Raise risk signals
   for (site, date), count in capacity_hits.items():
       if count >= 3:
           risks.append({
               "type": "capacity_pressure",
               "site": site,
               "date": date,
               "severity": "high",
               "message": (
                   f"Repeated capacity blocks detected for "
                   f"site={site} on date={date}"
               ),
           })

   return risks