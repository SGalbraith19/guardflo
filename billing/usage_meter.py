from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from models.tenant import Tenant
from tenancy.models import UsageRecord


def get_usage_for_update(db: Session, tenant_id: int) -> UsageRecord:
   """
   Locks the tenant usage row using SELECT FOR UPDATE.
   Prevents concurrent quota overspending.
   """

   stmt = (
       select(UsageRecord)
       .where(UsageRecord.tenant_id == tenant_id)
       .with_for_update()
   )

   result = db.execute(stmt).scalar_one_or_none()

   if not result:
       raise Exception("Usage record not found")

   return result


def increment_usage_atomic(db: Session, tenant_id: int):
   """
   Fully atomic usage increment.

   - Opens DB transaction
   - Locks row
   - Enforces quota
   - Increments usage
   - Commits safely
   """

   try:
       with db.begin():  # 🔒 START TRANSACTION

           # Lock usage row
           usage = get_usage_for_update(db, tenant_id)

           # Get tenant (same transaction)
           tenant = db.query(Tenant).filter(
               Tenant.id == tenant_id
           ).one()

           # 🚫 Enforce quota BEFORE increment
           if usage.current_period_usage >= tenant.quota_limit:
               raise Exception("Quota exceeded")

           # Increment safely
           usage.current_period_usage += 1

   except Exception:
       db.rollback()
       raise