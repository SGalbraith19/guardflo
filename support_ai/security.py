import hmac
import hashlib
import json
from datetime import datetime

SECRET_KEY = "super-enterprise-secret"


def sign_quote(payload: dict) -> str:
   message = json.dumps(payload, sort_keys=True).encode()
   signature = hmac.new(
       SECRET_KEY.encode(),
       message,
       hashlib.sha256
   ).hexdigest()
   return signature