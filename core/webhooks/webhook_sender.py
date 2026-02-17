import hmac
import hashlib
import json
import time
import requests

def sign_payload(secret: str, payload: bytes) -> str:
   signature = hmac.new(
       secret.encode(),
       payload,
       hashlib.sha256
   ).hexdigest()
   return f"sha256={signature}"


def send_webhook(url: str, secret: str, payload: dict):
   body = json.dumps(payload).encode()

   headers = {
       "Content-Type": "application/json",
       "X-Signature": sign_payload(secret, body),
   }

   retries = [1, 5, 15]  # seconds

   for delay in retries:
       try:
           response = requests.post(
               url,
               data=body,
               headers=headers,
               timeout=5
           )
           if response.status_code < 400:
               return
       except Exception:
           time.sleep(delay)
