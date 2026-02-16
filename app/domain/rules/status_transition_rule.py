from app.domain.rules.base import Rule
from app.domain.status_validation import validate_status_transition
from app.domain.decision import Decision

class StatusTransitionRule(Rule):
   rule_id = "VALID_STATUS_TRANSITION"

   def evaluate(self, *, booking, actor_id: str, context: dict, db=None) -> Decision:
       try:
           return validate_status_transition(
               current_status=booking.status,
               new_status=context["new_status"],
               entity_id=booking.id,
               actor_id=actor_id,
           )
       except Exception as exc:
           return Decision.deny(
               rule_id=self.rule_id,
               reason=str(exc),
               consequence="Status transition blocked",
               context=context,
               rule_evaluations={},
               entity_type="booking",
               entity_id=booking.id,
               actor_id=actor_id,
           )