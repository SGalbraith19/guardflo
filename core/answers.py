# support_ai/answers.py

from models.schemas import QuestionType


ANSWER_CONSTRAINTS = {
   QuestionType.PRICING: {
       "allowed": [
           "indicative pricing ranges",
           "factors influencing pricing",
           "statement that pricing is non-binding",
       ],
       "forbidden": [
           "discounts",
           "promotions",
           "commitments",
           "payment instructions",
       ],
       "tone": "neutral, factual, non-persuasive",
   },

   QuestionType.GUARANTEES: {
       "allowed": [
           "uptime guarantees explanation",
           "audit retention explanation",
           "incident response scope",
           "difference between supported and unsupported operation",
       ],
       "forbidden": [
           "guarantee activation",
           "service level commitments",
           "legal assurances",
       ],
       "tone": "precise, conservative, formal",
   },

   QuestionType.CONTRACTS: {
       "allowed": [
           "how contracts are formed",
           "what a supported agreement includes",
           "steps required to enter a contract",
       ],
       "forbidden": [
           "signing on behalf of parties",
           "final terms",
           "legal advice",
       ],
       "tone": "procedural, neutral",
   },

   QuestionType.PAYMENTS: {
       "allowed": [
           "payment methods description",
           "billing cadence explanation",
           "what happens after payment",
       ],
       "forbidden": [
           "processing payments",
           "collecting payment details",
           "invoicing",
       ],
       "tone": "informational",
   },

   QuestionType.GENERAL: {
       "allowed": [
           "system behaviour explanation",
           "support boundaries",
           "responsibility clarification",
       ],
       "forbidden": [
           "enforcement overrides",
           "policy changes",
           "optimisation advice",
       ],
       "tone": "authoritative, neutral",
   },
}


def get_answer_constraints(question_type: QuestionType) -> dict:
   """
   Returns the allowed and forbidden answer surface
   for a given question type.
   """
   return ANSWER_CONSTRAINTS[question_type]