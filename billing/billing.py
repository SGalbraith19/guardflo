import stripe
import os
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import func
from database import SessionLocal
from tenancy.models import FinancialDecision

# Set from environment variable in production
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_yourkey")

def get_monthly_usage(org_name):
   db = SessionLocal()
   try:
       start = datetime.utcnow().replace(day=1)
       count = db.query(func.count(FinancialDecision.id)).filter(
           FinancialDecision.organisation == org_name,
           FinancialDecision.created_at >= start
       ).scalar()
       return count
   finally:
       db.close()

def create_customer(email: str, organisation: str):
   try:
       customer = stripe.Customer.create(
           email=email,
           name=organisation,
           metadata={"organisation": organisation}
       )
       return customer
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))


def create_subscription(customer_id: str, price_id: str):
   try:
       subscription = stripe.Subscription.create(
           customer=customer_id,
           items=[{"price": price_id}],
           payment_behavior="default_incomplete",
           expand=["latest_invoice.payment_intent"],
       )
       return subscription
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))
   
def create_checkout_session(amount: int, organisation: str):
   try:
       session = stripe.checkout.Session.create(
           payment_method_types=["card"],
           mode="payment",
           line_items=[{
               "price_data": {
                   "currency": "usd",
                   "product_data": {
                       "name": f"{organisation} Subscription",
                   },
                   "unit_amount": amount,
               },
               "quantity": 1,
           }],
           success_url="http://localhost:3000/success",
           cancel_url="http://localhost:3000/cancel",
           metadata={
               "organisation": organisation
           }
       )

       return session.url

   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))