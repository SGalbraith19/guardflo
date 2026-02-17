# app/domain/webhook_dispatcher.py

import json
import hmac
import hashlib
import requests

from core.config import get_settings
from tenancy.models import WebhookSubscription, WebhookDelivery


def _sign_payload(secret: str, payload: str) -> str:
   """
   Create HMAC-SHA256 signature for webhook payload.
   """
   return hmac.new(
       secret.encode(),
       payload.encode(),
       hashlib.sha256,
   ).hexdigest()


def dispatch_webhook(db, event_type: str, payload: dict) -> None:
   """
   First-class domain event dispatcher.

   Guarantees:
   - Never raises to caller
   - Never blocks domain logic
   - Always records delivery attempts
   - Respects environment configuration
   """

   settings = get_settings()

   # ---- ENVIRONMENT GUARD ----
   if not settings.ENABLE_WEBHOOKS:
       return

   # Load active subscriptions for this event
   subscriptions = (
       db.query(WebhookSubscription)
       .filter(
           WebhookSubscription.event == event_type,
           WebhookSubscription.is_active.is_(True),
       )
       .all()
   )

   if not subscriptions:
       return

   payload_json = json.dumps(payload)

   for subscription in subscriptions:
       signature = _sign_payload(
           subscription.secret,
           payload_json,
       )

       success = False
       status_code = None

       try:
           response = requests.post(
               subscription.target_url,
               data=payload_json,
               headers={
                   "Content-Type": "application/json",
                   "X-Event-Type": event_type,
                   "X-Signature": signature,
               },
               timeout=settings.WEBHOOK_TIMEOUT_SECONDS,
           )

           status_code = str(response.status_code)
           success = response.ok

       except Exception:
           # Swallow all exceptions – domain logic must never fail
           success = False

       # ---- IMMUTABLE DELIVERY LOG ----
       delivery = WebhookDelivery(
           subscription_id=subscription.id,
           event=event_type,
           payload=payload_json,
           status_code=status_code,
           success=success,
       )

       db.add(delivery)

   # Commit delivery evidence only
   db.commit()