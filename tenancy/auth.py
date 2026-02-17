from fastapi import Header, HTTPException
from tenancy.service import resolve_organisation


def verify_api_key(x_api_key: str = Header(...)):

   org = resolve_organisation(x_api_key)

   if not org:
       raise HTTPException(status_code=403, detail="Invalid API key")
   
   if not org.subscription_active:
       raise HTTPException(status_code=403, detail="Subscription inactive")

   return org