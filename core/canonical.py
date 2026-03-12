import json
from typing import Any


def canonical_json(data: Any) -> str:
   """
   Deterministic JSON serialization.
   - Sorted keys
   - No whitespace
   - UTF-8 safe
   """

   return json.dumps(
       data,
       sort_keys=True,
       separators=(",", ":"),
       ensure_ascii=False,
   )