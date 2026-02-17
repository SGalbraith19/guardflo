# support_ai/guarantee_context.py

def build_guarantee_context() -> str:
   """
   Explains why support guarantees exist and what problems they address.
   This is educational, not promotional.
   """

   return """
Support guarantees exist to address operational risk, not convenience.

Uptime guarantees formalise responsibility for system availability,
ensuring that failures are treated as incidents rather than best-effort issues.

Audit retention guarantees ensure that enforcement decisions remain
provable, reviewable, and defensible over time, particularly in regulated
or high-liability environments.

Incident response obligations ensure that failures are acknowledged,
triaged, and addressed within defined timeframes by accountable parties.

Organisations typically value these guarantees when enforcement outcomes
are business-critical, externally visible, or subject to audit.

These guarantees do not change system behaviour.
They change responsibility and accountability.
""".strip()