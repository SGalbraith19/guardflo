import pytest
from uuid import uuid4

from app.domain.bookings import update_booking_status
from app.domain.enforcement import EnforcementError
from app.models import Booking, BookingStatus


def test_valid_status_transition_emits_event(db_session):
   booking = Booking()
   db_session.add(booking)
   db_session.commit()

   actor_id = str(uuid4())

   event = update_booking_status(
       db=db_session,
       booking=booking,
       new_status=BookingStatus.CONFIRMED,
       actor_id=actor_id,
       decision_context={"source": "test"},
   )

   assert booking.status == BookingStatus.CONFIRMED.value
   assert event["previous_state"] == BookingStatus.PENDING.value
   assert event["new_state"] == BookingStatus.CONFIRMED.value
   assert event["actor_id"] == actor_id
   assert event["decision_context"]["source"] == "test"
   assert "timestamp" in event


def test_invalid_status_transition_raises_error(db_session):
   booking = Booking()
   booking.status = BookingStatus.CANCELLED.value

   db_session.add(booking)
   db_session.commit()

   with pytest.raises(EnforcementError):
       update_booking_status(
           db=db_session,
           booking=booking,
           new_status=BookingStatus.CONFIRMED,
           actor_id="tester",
           decision_context={"source": "test"},
       )


def test_terminal_states_cannot_transition(db_session):
   booking = Booking()
   booking.status = BookingStatus.COMPLETED.value

   db_session.add(booking)
   db_session.commit()

   with pytest.raises(EnforcementError):
       update_booking_status(
           db=db_session,
           booking=booking,
           new_status=BookingStatus.CANCELLED,
           actor_id="tester",
           decision_context={"source": "test"},
       )


def test_decision_context_is_mandatory(db_session):
   booking = Booking()
   db_session.add(booking)
   db_session.commit()

   with pytest.raises(EnforcementError):
       update_booking_status(
           db=db_session,
           booking=booking,
           new_status=BookingStatus.CONFIRMED,
           actor_id="tester",
           decision_context={},
       )