# support_ai/audit.py

from datetime import datetime
import json
import os

AUDIT_FILE = "support_ai/logs/audit.log"

os.makedirs("support_ai/logs", exist_ok=True)

def record_support_event(event: dict):
   record = {
       "timestamp": datetime.utcnow().isoformat(),
       **event
   }

   with open(AUDIT_FILE, "a") as f:
       f.write(json.dumps(record) + "\n")


def read_audit_events(limit: int = 50):
   if not os.path.exists(AUDIT_FILE):
       return []

   with open(AUDIT_FILE, "r") as f:
       lines = f.readlines()[-limit:]

   return [json.loads(line) for line in lines]