import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(amount: int, organisation_name: str, id: int):
   session = stripe.checkout.Session.create(
       payment_method_types=["card"],
       mode="payment",
       line_items=[
           {
               "price_data": {
                   "currency": "usd",
                   "product_data": {
                       "name": f"GuardFlo Enterprise Plan - {organisation_name}",
                   },
                   "unit_amount": amount,
               },
               "quantity": 1,
           }
       ],
       metadata={
           "org_id": id
       },
       success_url="http://localhost:8000/success",
       cancel_url="http://localhost:8000/cancel",
   )

   return session.url