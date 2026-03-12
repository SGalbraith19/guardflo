import os
import json
import uuid
import time
import hmac
import hashlib

from security.key_registry import (
   get_active_key,
   ACTIVE_KEY_VERSION,
   get_key,
)


# ==========================================================
# SIGN DECISION
# ==========================================================

def sign_decision(payload: dict) -> dict:
   """
   Signs a decision payload using the active HMAC key.

   Adds:
   - decision_id
   - timestamp
   - key_version
   - signature
   """

   decision_id = str(uuid.uuid4())
   timestamp = int(time.time())
   nonce = str(uuid.uuid4())

   signed_payload = {
       "decision_id": decision_id,
       "timestamp": timestamp,
       "nonce": nonce,
       "key_version": ACTIVE_KEY_VERSION,
       **payload,
   }

   # Deterministic canonical JSON
   message = json.dumps(
       signed_payload,
       separators=(",", ":"),
       sort_keys=True,
       default=str,
   ).encode()

   key = get_active_key()

   signature = hmac.new(
       key.encode(),
       message,
       hashlib.sha256,
   ).hexdigest()

   signed_payload["signature"] = signature

   return signed_payload


# ==========================================================
# VERIFY DECISION
# ==========================================================

def verify_decision(signed_payload: dict) -> bool:
   """
   Verifies a signed decision using the embedded key_version.
   """

   signature = signed_payload.get("signature")
   key_version = signed_payload.get("key_version")

   if not signature or not key_version:
       return False

   # Remove signature before recomputing
   unsigned_payload = signed_payload.copy()
   unsigned_payload.pop("signature")

   message = json.dumps(
       unsigned_payload,
       separators=(",", ":"),
       sort_keys=True,
       default=str,
   ).encode()

   try:
       key = get_key(key_version)
   except Exception:
       return False

   expected_signature = hmac.new(
       key.encode(),
       message,
       hashlib.sha256,
   ).hexdigest()

   return hmac.compare_digest(signature, expected_signature)