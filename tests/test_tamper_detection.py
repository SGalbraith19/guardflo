from signing.signer import sign_decision, verify_decision


def test_signature_valid():
   payload = {"amount": 100, "currency": "USD"}

   signed = sign_decision(payload)

   assert verify_decision(signed) is True


def test_signature_tampered():
   payload = {"amount": 100, "currency": "USD"}

   signed = sign_decision(payload)

   # Tamper with data
   signed["amount"] = 999999

   assert verify_decision(signed) is False


def test_signature_wrong_key_version():
   payload = {"amount": 100, "currency": "USD"}

   signed = sign_decision(payload)

   signed["key_version"] = "v999"

   assert verify_decision(signed) is False