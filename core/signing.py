import hmac
import hashlib
import json
import os

SECRET = os.getenv("DECISION_SIGNING_SECRET")

if not SECRET:
   raise RuntimeError("DECISION_SIGNING_SECRET not set")


def sign_decision(payload: dict) -> str:
   canonical = json.dumps(payload, sort_keys=True)
   signature = hmac.new(
       SECRET.encode(),
       canonical.encode(),
       hashlib.sha256
   ).hexdigest()

   return signature