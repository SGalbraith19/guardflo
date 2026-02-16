from abc import ABC, abstractmethod
from app.domain.decision import Decision

class Rule(ABC):
   """
   Base class for all deterministic enforcement rules.
   """

   rule_id: str

   @abstractmethod
   def evaluate(self, *, booking, actor_id: str, context: dict, db=None) -> Decision:
       pass