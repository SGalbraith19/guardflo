from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.api_key import APIKey
from models.tenant import Tenant
import hashlib


def hash_key(raw_key: str):
   return hashlib.sha256(raw_key.encode()).hexdigest()


def get_current_tenant(
   x_api_key: str = Header(None),
   db: Session = Depends(get_db)
):
   if not x_api_key:
       raise HTTPException(status_code=401, detail="API key required")

   key_hash = hash_key(x_api_key)

   api_key = db.query(APIKey).filter(
       APIKey.key_hash == key_hash,
       APIKey.active == True
   ).first()

   if not api_key:
       raise HTTPException(status_code=401, detail="Invalid API key")

   tenant = db.query(Tenant).filter(Tenant.id == api_key.tenant_id).first()

   return tenant