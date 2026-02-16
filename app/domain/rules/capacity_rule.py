from app.config import get_settings
from app.domain.decision import Decision


class CapacityException(Exception):
   pass


def enforce_capacity(
   *,
   db,
   booking,
   actor_id: str,
) -> Decision:

   settings = get_settings()

   if not settings.ENABLE_CAPACITY_ENFORCEMENT:
       return Decision.allow(
           rule_id="CAPACITY_DISABLED",
           reason="Capacity enforcement disabled",
           consequence=None,
           context={},
           rule_evaluations={},
           entity_type="booking",
           entity_id=booking.id,
           actor_id=actor_id,
       )

   # If booking has no max_capacity, treat as unlimited
   max_capacity = getattr(booking, "max_capacity", None)

   if not max_capacity or max_capacity <= 0:
       return Decision.allow(
           rule_id="NO_CAPACITY_LIMIT",
           reason="No capacity limit defined",
           consequence=None,
           context={},
           rule_evaluations={},
           entity_type="booking",
           entity_id=booking.id,
           actor_id=actor_id,
       )

   from app.models import Booking

   ACTIVE_STATUSES = {"pending", "confirmed"}

   query = (
       db.query(Booking)
       .filter(
           Booking.deleted_at.is_(None),
           Booking.status.in_(ACTIVE_STATUSES),
           Booking.site == booking.site,
           Booking.job_role == booking.job_role,
           Booking.start_date == booking.start_date,
       )
   )

   current_count = query.count()

   if current_count >= max_capacity:
       return Decision.deny(
           rule_id="CAPACITY_EXCEEDED",
           reason="Capacity exceeded",
           consequence="Booking blocked",
           context={
               "site": booking.site,
               "role": booking.job_role,
               "date": str(booking.start_date),
               "max_capacity": booking.max_capacity,
               "current_count": current_count,
           },
           rule_evaluations={},
           entity_type="booking",
           entity_id=booking.id,
           actor_id=actor_id,
       )

   return Decision.allow(
       rule_id="CAPACITY_OK",
       reason="Capacity available",
       consequence=None,
       context={},
       rule_evaluations={},
       entity_type="booking",
       entity_id=booking.id,
       actor_id=actor_id,
   )