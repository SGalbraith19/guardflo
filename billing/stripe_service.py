import os
import secrets
from click.globals import pop_context
import stripe

from fastapi import APIRouter, Request, HTTPException, Form
from database import SessionLocal
from tenancy.models import Organisation
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# =========================================================
# STRIPE CONFIG
# =========================================================

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# =========================================================
# TIER CONFIG
# =========================================================

TIER_LIMITS = {
   "starter": "price_1T5gQsBjtjn8xWYF4Kgp2Irk",
   "pro": "price_1T5gRIBjtjn8xWYFeI833jEe",
   "enterprise": "price_1T5gRjBjtjn8xWYFuuPsx3h5",
}

# =========================================================
# CREATE CHECKOUT SESSION
# =========================================================

@router.post("/create-checkout-session")
async def create_checkout_session(
   company_name: str = Form(...),
   plan: str = Form(...),
   customer_email: str = Form(...),
   price_id: str = Form(...)
):
   """
   Creates Stripe checkout session.
   Organisation is NOT created yet.
   It is created only after successful payment via webhook.
   """

   if plan not in TIER_LIMITS:
       raise HTTPException(status_code=400, detail="Invalid plan")
   
   price_id = TIER_LIMITS[plan]

   try:
       session = stripe.checkout.Session.create(
           payment_method_types=["card"],
           mode="subscription",
           customer_email=customer_email,
           line_items=[
               {
                   "price": price_id,
                   "quantity": 1,
               }
           ],
           metadata={
               "company_name": company_name,
               "plan": plan,
           },
           success_url="http://127.0.0.1:8000/success",
           cancel_url="http://127.0.0.1:8000/pricing",
       )

       return RedirectResponse(session.url, status_code=303)

   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))


# =========================================================
# STRIPE WEBHOOK
# =========================================================

@router.post("/webhook")
async def stripe_webhook(request: Request):

   payload = await request.body()
   sig_header = request.headers.get("stripe-signature")

   try:
       event = stripe.Webhook.construct_event(
           payload,
           sig_header,
           endpoint_secret,
       )
   except Exception:
       raise HTTPException(status_code=400, detail="Invalid webhook signature")

   db = SessionLocal()

   try:
       event_type = event["type"]

       # =================================================
       # CHECKOUT COMPLETED → CREATE TENANT
       # =================================================
       if event_type == "checkout.session.completed":

           session = event["data"]["object"]

           company_name = session.get("metadata", {}).get("company_name")
           plan = session.get("metadata", {}).get("plan")
           customer_id = session.get("customer")

           if not company_name or not plan:
               return {"status": "missing metadata"}

           # Prevent duplicate tenant creation
           existing = None                

           # Generate API key
           
           raw_api_key = "sk_live_" + secrets.token_hex(24)
           print("NEW API KEY:", raw_api_key)

           hashed_key = pop_context.hash(raw_api_key)

           # Create Organisation
           org = Organisation(
               id="org_" + secrets.token_hex(8),
               org_name=company_name,
               tier=plan,
               active=True,
               stripe_customer_id=customer_id,
               api_key=hashed_key,
               quota_limit=TIER_LIMITS.get(plan, 1000),
           )

           db.add(org)
           db.commit()

       # =================================================
       # PAYMENT FAILED → DISABLE TENANT
       # =================================================
       elif event_type == "invoice.payment_failed":

           invoice = event["data"]["object"]
           customer_id = invoice.get("customer")

           org = db.query(Organisation).filter(
               Organisation.stripe_customer_id == customer_id
           ).first()

           if org:
               org.active = False
               db.commit()

       # =================================================
       # SUBSCRIPTION CANCELLED → DISABLE TENANT
       # =================================================
       elif event_type == "customer.subscription.deleted":

           subscription = event["data"]["object"]
           customer_id = subscription.get("customer")

           org = db.query(Organisation).filter(
               Organisation.stripe_customer_id == customer_id
           ).first()

           if org:
               org.active = False
               db.commit()

        
       elif event_type == "customer.subscription.updated":
        
            subscription = event["data"]["object"]
            customer_id = subscription.get("customer")

            org = db.query(Organisation).filter(
            Organisation.stripe_customer_id == customer_id
            ).first()

            if org:
               org.active = subscription["status"] == "active"
               db.commit()

   except Exception as e:
       db.rollback()
       raise HTTPException(status_code=500, detail=str(e))

   finally:
       db.close()

   return {"status": "success"}

# ============================================================
# SUCCESS PAGE
# ============================================================

@router.get("/success")
async def checkout_success(request: Request, session_id: str):
   session = stripe.checkout.Session.retrieve(session_id)

   return templates.TemplateResponse(
       "success.html",
       {
           "request": request,
           "email": session.get("customer_email")
       }
   )

@router.post("/portal")
def create_portal_session(customer_id: str):
   session = stripe.billing_portal.Session.create(
       customer=customer_id,
       return_url="http://localhost:8000"
   )
   return {"url": session.url}

@router.get("/", response_class=HTMLResponse)
async def landing(request: Request):
   return templates.TemplateResponse("landing.html", {"request": request})

@router.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
   return templates.TemplateResponse("pricing.html", {"request": request})

@router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
   return templates.TemplateResponse("terms.html", {"request": request})