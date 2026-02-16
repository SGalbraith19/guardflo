import os
from typing import Optional
from support_ai.tenancy_models import Organisation
from support_ai.tenancy_db import SessionLocal

DEPLOYMENT_MODE = os.getenv("GUARDFLO_MODE", "multi")


def resolve_organisation(api_key: str) -> Optional[Organisation]:

   if DEPLOYMENT_MODE == "dedicated":
       # Dedicated mode ignores API key
       return Organisation(
           org_id=os.getenv("GUARDFLO_ORG_ID", "org_dedicated"),
           org_name=os.getenv("GUARDFLO_ORG_NAME", "DedicatedEnterprise"),
           tier=os.getenv("GUARDFLO_ORG_TIER", "large"),
           api_key="dedicated",
           active=True,
       )

   db = SessionLocal()

   try:
       org = db.query(Organisation).filter(
           Organisation.api_key == api_key
       ).first()

       if not org:
           return None

       if not org.active:
           return None

       return org

   finally:
       db.close()