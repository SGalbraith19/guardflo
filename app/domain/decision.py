from __future__ import annotations
from datetime import datetime
from typing import Any, Dict


class Decision:

   def __init__(
       self,
       *,
       entity_type: str,
       entity_id: Any,
       actor_id: str,
       rule_id: str,
       outcome: str,
       reason: str,
       consequence: str | None,
       context: Dict[str, Any],
       rule_evaluations: Dict[str, Any],
       evaluated_at: str | None = None,
   ):
       self.entity_type = entity_type
       self.entity_id = entity_id
       self.actor_id = actor_id
       self.rule_id = rule_id
       self.outcome = outcome
       self.reason = reason
       self.consequence = consequence
       self.context = context
       self.rule_evaluations = rule_evaluations
       self.evaluated_at = evaluated_at or datetime.utcnow().isoformat()


   @classmethod
   def allow(
       cls,
       *,
       rule_id: str,
       reason: str,
       consequence: str | None,
       context: Dict[str, Any],
       rule_evaluations: Dict[str, Any],
       entity_type: str,
       entity_id: Any,
       actor_id: str,
   ) -> "Decision":
       return cls(
           entity_type=entity_type,
           entity_id=entity_id,
           actor_id=actor_id,
           rule_id=rule_id,
           outcome="allowed",
           reason=reason,
           consequence=consequence,
           context=context,
           rule_evaluations=rule_evaluations,
       )

   @classmethod
   def deny(
       cls,
       *,
       rule_id: str,
       reason: str,
       consequence: str,
       context: Dict[str, Any],
       rule_evaluations: Dict[str, Any],
       entity_type: str,
       entity_id: Any,
       actor_id: str,
   ) -> "Decision":
       return cls(
           entity_type=entity_type,
           entity_id=entity_id,
           actor_id=actor_id,
           rule_id=rule_id,
           outcome="denied",
           reason=reason,
           consequence=consequence,
           context=context,
           rule_evaluations=rule_evaluations,
       )

   def to_dict(self) -> Dict[str, Any]:
       return {
           "entity_type": self.entity_type,
           "entity_id": self.entity_id,
           "actor_id": self.actor_id,
           "rule_id": self.rule_id,
           "outcome": self.outcome,
           "reason": self.reason,
           "consequence": self.consequence,
           "context": self.context,
           "rule_evaluations": self.rule_evaluations,
           "evaluated_at": self.evaluated_at,
       }