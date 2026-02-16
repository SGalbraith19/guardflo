from app.domain.enforcement import EnforcementError
from app.domain.decision import Decision

class RuleEngine:
   def __init__(self, rules):
       self.rules = rules

   def evaluate(self, *, booking, actor_id: str, context: dict, db=None) -> Decision:
       evaluations = {}

       for rule in self.rules:
           decision = rule.evaluate(
               booking=booking,
               actor_id=actor_id,
               context=context,
               db=db,
           )

           evaluations[rule.rule_id] = decision.to_dict()

           if decision.outcome != "allowed":
               raise EnforcementError(decision)

       return Decision.allow(
           rule_id="ALL_RULES_PASSED",
           reason="All rules allowed",
           consequence=None,
           context=context,
           rule_evaluations=evaluations,
           entity_type="booking",
           entity_id=booking.id,
           actor_id=actor_id,
       )