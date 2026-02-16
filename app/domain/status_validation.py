from app.models import BookingStatus
from app.domain.decision import Decision


VALID_TRANSITIONS = {
   BookingStatus.PENDING: {
       BookingStatus.CONFIRMED,
       BookingStatus.CANCELLED,
   },
   BookingStatus.CONFIRMED: {
       BookingStatus.CONFIRMED,
       BookingStatus.CANCELLED,
   },
   BookingStatus.COMPLETED: set(),
   BookingStatus.CANCELLED: set(),
}

def validate_status_transition(
   *,
   current_status: BookingStatus,
   new_status: BookingStatus,
   entity_id: int,
   actor_id: str,
) -> Decision:

   if current_status not in VALID_TRANSITIONS:
       return Decision.deny(
           rule_id="UNKNOWN_CURRENT_STATUS",
           reason=f"Unknown current status: {current_status}",
           consequence="Transition blocked",
           context={},
           rule_evaluations={},
           entity_type="booking",
           entity_id=entity_id,
           actor_id=actor_id,
       )

   allowed = VALID_TRANSITIONS[current_status]

   if new_status not in allowed:
       return Decision.deny(
           rule_id="INVALID_TRANSITION",
           reason=f"Invalid status transition: {current_status} -> {new_status}",
           consequence="Transition blocked",
           context={},
           rule_evaluations={},
           entity_type="booking",
           entity_id=entity_id,
           actor_id=actor_id,
       )

   return Decision.allow(
       rule_id="VALID_TRANSITION",
       reason="Status transition allowed",
       consequence=None,
       context={},
       rule_evaluations={},
       entity_type="booking",
       entity_id=entity_id,
       actor_id=actor_id,
   )