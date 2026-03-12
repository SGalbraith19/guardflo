from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from models.usage import Usage


def increment_usage(tenant_id, quota):
   """
   Atomic monthly quota enforcement.
   """

   session = SessionLocal()

   try:
       now = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

       usage = session.query(Usage).filter_by(
           tenant_id=tenant_id,
           period_start=now
       ).with_for_update().first()

       if not usage:
           usage = Usage(
               tenant_id=tenant_id,
               period_start=now,
               calls=0
           )
           session.add(usage)

       usage.calls += 1

       if usage.calls > quota:
           session.rollback()
           return False

       session.commit()
       return True

   except SQLAlchemyError:
       session.rollback()
       raise
   finally:
       session.close()