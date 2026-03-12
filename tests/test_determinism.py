import pytest
from uuid import uuid4
from datetime import datetime

from api.main import run_financial_decision
from tenancy.models import Organisation
from database import SessionLocal


def build_test_org():
   return Organisation(
       id=str(uuid4()),
       org_name="Determinism Test",
       tier="starter",
       subscription_active=True,
       api_key="test_key",
   )


def build_test_request():
   return {
       "amount": 500,
       "nonce": str(uuid4()),
       "policy_version": "v1"
   }


def test_engine_is_deterministic():
   """
   Same input → same output.
   """

   db = SessionLocal()

   org = build_test_org()

   request_payload = build_test_request()

   result1 = run_financial_decision(request_payload, org, policy=None)
   result2 = run_financial_decision(request_payload, org, policy=None)

   assert result1["approved"] == result2["approved"]
   assert result1["risk_score"] == result2["risk_score"]
   assert result1["violations"] == result2["violations"]
   assert result1["explanation"] == result2["explanation"]


def test_engine_output_stability_hash():
   """
   Deterministic output must produce stable canonical hash.
   """

   db = SessionLocal()

   org = build_test_org()

   request_payload = build_test_request()

   result1 = run_financial_decision(request_payload, org, policy=None)
   result2 = run_financial_decision(request_payload, org, policy=None)

   import json
   import hashlib

   def canonical_hash(data):
       return hashlib.sha256(
           json.dumps(data, sort_keys=True).encode()
       ).hexdigest()

   assert canonical_hash(result1) == canonical_hash(result2)

