from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime, UTC


@dataclass(frozen=True)
class BookingEvent:
   booking_id: str
   previous_state: str
   new_state: str
   actor_id: str
   decision_context: Dict[str, Any]
   timestamp: str | None = None

   def __post_init__(self):
       if self.timestamp is None:
           object.__setattr__(
               self,
               "timestamp",
               datetime.now(UTC).isoformat()
           )

   def to_dict(self) -> Dict[str, Any]:
       return {
           "booking_id": self.booking_id,
           "previous_state": self.previous_state,
           "new_state": self.new_state,
           "actor_id": self.actor_id,
           "decision_context": self.decision_context,
           "timestamp": self.timestamp,
       }