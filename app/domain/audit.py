from datetime import datetime
from typing import Dict


def record_enforcement(
   *,
   decision: str,
   entity_type: str,
   entity_id: int,
   actor_id: str,
   context: Dict,
) -> None:

   record = {
       "decision": decision,
       "entity_type": entity_type,
       "entity_id": entity_id,
       "actor_id": actor_id,
       "context": context,
       "timestamp": datetime.utcnow().isoformat(),
   }

   # Intentionally boring.
   # Replace print() later with durable sink.
   print(f"[ENFORCEMENT] {record}")