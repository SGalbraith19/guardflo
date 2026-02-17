# support_ai/disclosure.py

DISCLOSURE_STATEMENT = (
   "This enforcement support instance is running without uptime guarantees, "
   "audit retention guarantees, or incident response obligations."
)


def get_disclosure() -> str:
   """
   Returns a factual, non-persuasive disclosure about the support tier.

   This statement:
   - Is not a warning
   - Is not a call to action
   - Does not mention pricing
   - Is safe to forward verbatim
   """
   return DISCLOSURE_STATEMENT