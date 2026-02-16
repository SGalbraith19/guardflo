from enum import Enum


class BookingStatus(str, Enum):
   PENDING = "pending"
   CONFIRMED = "confirmed"
   CANCELLED = "cancelled"
   COMPLETED = "completed"

   @classmethod
   def terminal_states(cls) -> set["BookingStatus"]:
       return {
           cls.CANCELLED,
           cls.COMPLETED,
       }