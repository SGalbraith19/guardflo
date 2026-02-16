from datetime import datetime
from app.models import Booking, BookingEvent, BookingStatus
from app.database import SessionLocal


ALLOWED_TRANSITIONS = {
   BookingStatus.PENDING.value: {
       BookingStatus.CONFIRMED.value,
       BookingStatus.CANCELLED.value,
   },
   BookingStatus.CONFIRMED.value: {
       BookingStatus.COMPLETED.value,
       BookingStatus.CANCELLED.value,
   },
}

def transition_booking(
   *,
   booking,
   new_status,
   actor_id,
   decision_context,
   rule_evaluations,
):
   # no-op transition
   if booking.status == new_status:
       raise ValueError("No-op transition is not allowed")

   allowed = ALLOWED_TRANSITIONS.get(booking.status, set())
   if new_status not in allowed:
       raise ValueError(
           f"Invalid transition from {booking.status} to {new_status}"
       )

   previous = booking.status

   # Apply state change
   booking.status = new_status
   booking.updated_at = datetime.utcnow()

   # Emit immutable event
   previous_status = booking.status

   booking.status = new_status
   booking.updated_at = datetime.utcnow()
   
   event = BookingEvent(
   booking_id=booking.id,
   old_status=booking.status,
   new_status=new_status,
   actor_id=actor_id,
   decision_context=decision_context,
   entity_type="booking",  # ✅ CORRECT
   entity_id=booking.id,
)

   return {
   "event_type": "booking_status_changed",
   "entity_type": event.entity_type,
   "entity_id": event.entity_id,
   "booking_id": event.booking_id,
   "previous_state": event.old_status,
   "new_state": event.new_status,
   "actor_id": event.actor_id,
   "decision_context": event.decision_context,
   "timestamp": event.timestamp,
}