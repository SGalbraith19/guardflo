from app.models import BookingStatus

TERMINAL_STATES = {
   BookingStatus.COMPLETED,
   BookingStatus.CANCELLED,
}

VALID_TRANSITIONS = {
   BookingStatus.PENDING: {
       BookingStatus.CONFIRMED,
       BookingStatus.CANCELLED,
   },
   BookingStatus.CONFIRMED: {
       BookingStatus.COMPLETED,
       BookingStatus.CANCELLED,
   },
}

def is_valid_transition(current_status: BookingStatus, new_status: BookingStatus) -> bool:
   return new_status in VALID_TRANSITIONS.get(current_status, set())