import os
from functools import lru_cache


class Settings:
   # ---- Environment ----
   ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")

   # ---- Database ----
   DATABASE_URL: str = os.getenv("DATABASE_URL")

   # ---- Webhooks ----
   WEBHOOK_TIMEOUT_SECONDS: int = int(
       os.getenv("WEBHOOK_TIMEOUT_SECONDS", "5")
   )

   # ---- Safety / Capacity Defaults ----
   DEFAULT_CAPACITY_LIMIT: int = int(
       os.getenv("DEFAULT_CAPACITY_LIMIT", "0")
   )

   # ---- Feature Flags ----
   ENABLE_WEBHOOKS: bool = os.getenv("ENABLE_WEBHOOKS", "true").lower() == "true"
   ENABLE_CAPACITY_ENFORCEMENT: bool = os.getenv("ENABLE_CAPACITY_ENFORCEMENT", "true").lower() == "true"

   # ---- AI (future-safe, not active) ----
   ENABLE_AI_SIGNALS: bool = os.getenv("ENABLE_AI_SIGNALS", "false").lower() == "true"


@lru_cache
def get_settings() -> Settings:
   return Settings()