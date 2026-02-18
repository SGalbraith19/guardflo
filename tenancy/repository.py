from sqlalchemy.orm import Session
from database import SessionLocal
from tenancy.models import Organisation


def get_tenant(tenant_id: str):
   db: Session = SessionLocal()
   try:
       return db.query(Organisation).filter(
           Organisation.id == tenant_id
       ).first()
   finally:
       db.close()