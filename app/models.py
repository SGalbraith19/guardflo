from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict

from sqlalchemy import Column, Integer, String
from app.database import Base
from app.domain.decision import Decision


class BookingStatus(str, Enum):
   PENDING = "pending"
   CONFIRMED = "confirmed"
   CANCELLED = "cancelled"
   COMPLETED = "completed"


class BookingEvent:
   """
   Immutable domain event.
   Behaves like a dict for contract tests.
   """

   def __init__(
       self,
       *,
       booking_id: int,
       previous_state: str,
       new_state: str,
       actor_id: str,
       decision_context: dict,
       decision: Decision | None = None,
       timestamp: str | None = None,
   ):
       self._data = {
           "event_type": "booking_status_changed",
           "entity_type": "booking",
           "entity_id": booking_id,
           "booking_id": booking_id,
           "previous_state": previous_state,
           "new_state": new_state,
           "actor_id": actor_id,
           "decision_context": decision_context,
           "decision": decision.to_dict() if decision else None,
           "timestamp": timestamp or datetime.utcnow().isoformat(),
       }


   def __getitem__(self, key):
       return self._data[key]

   def get(self, key, default=None):
       return self._data.get(key, default)

   def keys(self):
       return self._data.keys()

   def values(self):
       return self._data.values()

   def items(self):
       return self._data.items()

   def to_dict(self) -> dict:
       return dict(self._data)

   def __repr__(self):
       return f"BookingEvent({self._data})"


class Booking(Base):
   __tablename__ = "bookings"

   id = Column(Integer, primary_key=True)
   status = Column(String, nullable=False, default=BookingStatus.PENDING.value)
   updated_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())

   TERMINAL_STATES = {
       BookingStatus.CANCELLED.value,
       BookingStatus.COMPLETED.value,
   }

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

   def update_status(
       self,
       *,
       new_status: BookingStatus,
       actor_id: str,
       decision_context: dict,
       decision=None,
       rule_evaluations: dict | None = None,
   ) -> BookingEvent:
       
       if self.status in self.TERMINAL_STATES:
           raise ValueError("Terminal state cannot transition")

       allowed = self.ALLOWED_TRANSITIONS.get(self.status, set())
       if new_status.value not in allowed:
           raise ValueError("Invalid status transition")

       if not decision_context:
           raise ValueError("Decision context is mandatory")

       previous_state = self.status
       self.status = new_status.value
       self.updated_at = datetime.utcnow().isoformat()

       return BookingEvent(
           booking_id=self.id or 0,
           previous_state=previous_state,
           new_state=new_status.value,
           actor_id=actor_id,
           decision_context=decision_context,
           decision=decision,
       )