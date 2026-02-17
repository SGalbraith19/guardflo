import os
import hmac
import hashlib
import json

SECRET = os.environ.get("DECISION_SIGNING_SECRET")

if not SECRET:
   raise RuntimeError("DECISION_SIGNING_SECRET not set")


def _canonical(payload: dict) -> bytes:
   return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def sign_decision(payload: dict) -> str:
   message = _canonical(payload)
   return hmac.new(
       SECRET.encode(),
       message,
       hashlib.sha256
   ).hexdigest()


def verify_signature(payload: dict, signature: str) -> bool:
   message = _canonical(payload)
   expected = hmac.new(
       SECRET.encode(),
       message,
       hashlib.sha256
   ).hexdigest()

   return hmac.compare_digest(expected, signature)