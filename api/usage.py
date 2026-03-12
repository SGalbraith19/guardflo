from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException

from tenancy.models import UsageRecord


def enforce_usage(db: Session, tenant):
   current_month = datetime.utcnow().strftime("%Y-%m")

   usage = (
       db.query(UsageRecord)
       .filter(
           UsageRecord.tenant_id == tenant.id,
           UsageRecord.month == current_month,
       )
       .first()
   )

   if not usage:
       usage = UsageRecord(
           tenant_id=tenant.id,
           month=current_month,
           decision_count=0,
       )
       db.add(usage)
       db.commit()
       db.refresh(usage)

   # Quota enforcement
   if usage.decision_count >= tenant.quota:
       raise HTTPException(
           status_code=403,
           detail="Quota exceeded"
       )

   usage.decision_count += 1
   db.commit()

   return usage