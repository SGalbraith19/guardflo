from app.domain.decision import Decision
from app.domain.enforcement import EnforcementError
from app.domain.status_validation import validate_status_transition
from app.domain.rules.capacity_rule import enforce_capacity
from app.domain.audit import record_enforcement
from app.domain.events import BookingEvent
from app.domain.rules.engine import RuleEngine
from app.domain.rules.status_transition_rule import StatusTransitionRule
from app.domain.rules.capacity_rule import CapacityException



def enforce(decision: Decision):
   
   if decision.outcome != "allowed":
       raise EnforcementError(decision)


def update_booking_status(
   *,
   booking,
   new_status,
   actor_id: str,
   decision_context: dict,
   db=None,
):

   if not decision_context:
    raise EnforcementError(
       Decision.deny(
           rule_id="CONTEXT_REQUIRED",
           reason="decision_context is mandatory",
           consequence="Transition blocked",
           context={},
           rule_evaluations={},
           entity_type="booking",
           entity_id=booking.id,
           actor_id=actor_id,
       )
   )

   previous_state = booking.status

   engine = RuleEngine([
      StatusTransitionRule(),
      CapacityException(),
   ])

   engine.evaluate(
      booking=booking,
      actor_id=actor_id,
      context={
         "new_status":new_status,
         **decision_context,
      },
      db=db,
   )

   booking.status = new_status

   event = BookingEvent(
       booking_id=booking.id,
       previous_state=previous_state,
       new_state=new_status,
       actor_id=actor_id,
       decision_context=decision_context,
   )

   if db is not None:
       db.add(booking)
       db.commit()

   return event.to_dict()