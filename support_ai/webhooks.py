import stripe
import os
from fastapi import APIRouter, Request, HTTPException
from support_ai.tenancy_db import SessionLocal
from support_ai.tenancy_models import Organisation

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):

   payload = await request.body()
   sig_header = request.headers.get("stripe-signature")

   try:
       event = stripe.Webhook.construct_event(
           payload,
           sig_header,
           endpoint_secret
       )
   except Exception:
       raise HTTPException(status_code=400, detail="Invalid webhook signature")

   # ✅ HANDLE SUCCESSFUL CHECKOUT
   if event["type"] == "checkout.session.completed":

       session = event["data"]["object"]

       org_id = session["metadata"].get("org_id")
       selected_tier = session["metadata"].get("tier")

       db = SessionLocal()

       try:
           org = db.query(Organisation).filter(
               Organisation.id == org_id
           ).first()

           if org:
               org.tier = selected_tier
               org.subscriptions_active = True
               db.commit()

       finally:
           db.close()

   # ✅ FAILED PAYMENT HANDLING
   if event["type"] == "invoice.payment_failed":

       subscription = event["data"]["object"]
       customer = subscription.get("customer")

       # Optional: you can suspend here later
       # For now we just log it

       print("Payment failed for customer:", customer)

   return {"status": "success"}