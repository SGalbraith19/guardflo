from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tenancy.models import Base

from sqlalchemy.orm import Session
from database import SessionLocal
from tenancy.models import Organisation

DATABASE_URL = "sqlite:///./tenancy.db"

engine = create_engine(
   DATABASE_URL,
   connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
   autocommit=False,
   autoflush=False,
   bind=engine
)

def init_tenancy_db():
   Base.metadata.create_all(bind=engine)

def get_tenant(tenant_id: str):
   db: Session = SessionLocal()
   try:
      return db.query(Organisation).filter(Organisation.id == tenant_id).first()
   finally:
      db.close()