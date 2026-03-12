from uuid import UUID
from sqlalchemy.orm import Session
from database import SessionLocal
from tenancy.models import Organisation


def get_tenant(tenant_id: UUID):
   db: Session = SessionLocal()
   try:
       return db.query(Organisation).filter(
           Organisation.api_key == tenant_id
       ).first()
   finally:
       db.close()