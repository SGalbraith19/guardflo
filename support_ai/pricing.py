from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from support_ai.database import SessionLocal
from support_ai.models import Quote
from support_ai.security import sign_quote
from support_ai.auth import verify_api_key
from support_ai.pricing_engine import calculate_pricing

router = APIRouter()


class PricingInput(BaseModel):
   organisation_size: str
   production: bool
   sla_24_7: bool
   priority_response: bool = False


@router.post("/pricing/quote")
def generate_quote(
   data: PricingInput,
   org=Depends(verify_api_key)
):
   pricing = calculate_pricing(data)

   payload = {
       "organisation": org["organisation_name"],
       "tier": org["tier"],
       "base_price": pricing["base_price"],
       "final_price": pricing["final_price"],
       "production": data.production,
       "sla_24_7": data.sla_24_7,
       "timestamp": datetime.utcnow().isoformat()
   }

   signature = sign_quote(payload)

   db = SessionLocal()

   quote = Quote(
       organisation=org["organisation_name"],
       tier=org["tier"],
       base_price=pricing["base_price"],
       final_price=pricing["final_price"],
       production=data.production,
       sla_24_7=data.sla_24_7,
       applied_multipliers=pricing["applied_multipliers"],
       signature=signature
   )

   db.add(quote)
   db.commit()
   db.refresh(quote)
   db.close()

   return {
       "quote_id": quote.id,
       "signature": signature,
       "pricing": pricing
   }