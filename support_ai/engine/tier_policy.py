from typing import Dict

RATE_LIMITS = {
    "starter": "10/minute",
    "pro": "60/minute",
    "enterprise": "200/minute"
}

TIER_CAPABILITIES: Dict[str, dict] = {
   "starter": {
       "risk_scoring": False,
       "explainability": False,
       "audit_logging": False,
   },
   "growth": {
       "risk_scoring": True,
       "explainability": False,
       "audit_logging": True,
   },
   "enterprise": {
       "risk_scoring": True,
       "explainability": True,
       "audit_logging": True,
   },
}

TIER_LIMITS = {
   "starter": {
       "monthly_decisions": 1000,
       "rate_limit_per_minute": 30,
   },
   "pro": {
       "monthly_decisions": 10000,
       "rate_limit_per_minute": 120,
   },
   "enterprise": {
       "monthly_decisions": None,  # unlimited
       "rate_limit_per_minute": 500,
   }
}