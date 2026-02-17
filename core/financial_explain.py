def generate_explanation(violations: list) -> dict:
   if not violations:
       return {
           "what_was_invalid": None,
           "what_would_have_happened": "Transaction would proceed automatically.",
           "what_correct_looks_like": "Transaction meets all approval criteria."
       }

   return {
       "what_was_invalid": "; ".join(violations),
       "what_would_have_happened": "Transaction would have executed despite elevated financial risk.",
       "what_correct_looks_like": "Adjust transaction to comply with approval thresholds and risk limits."
   }