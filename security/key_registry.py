import os
from typing import Dict

# In-memory key store (runtime)
_KEYS: Dict[str, str] = {}

# Active key version
ACTIVE_KEY_VERSION = "v1"


def _load_initial_keys():
   """
   Load initial keys from environment.
   """
   v1 = os.getenv("HMAC_SECRET_V1")

   if not v1:
       raise RuntimeError("HMAC_SECRET_V1 must be set")

   _KEYS["v1"] = v1


_load_initial_keys()


def get_active_key() -> str:
   return _KEYS[ACTIVE_KEY_VERSION]


def get_key(version: str) -> str:
   key = _KEYS.get(version)
   if not key:
       raise RuntimeError(f"Unknown key version: {version}")
   return key


def rotate_key(new_version: str, new_secret: str):
   global ACTIVE_KEY_VERSION

   if new_version in _KEYS:
       raise RuntimeError("Key version already exists")

   _KEYS[new_version] = new_secret
   ACTIVE_KEY_VERSION = new_version