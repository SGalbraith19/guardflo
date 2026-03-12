import json
import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


# -----------------------------
# Load keys from environment
# -----------------------------

private_key_pem = os.getenv("PRIVATE_KEY")
public_key_pem = os.getenv("PUBLIC_KEY")

if not private_key_pem or not public_key_pem:
   raise RuntimeError("Signing keys not found in environment variables")

guardflo_private = serialization.load_pem_private_key(
   private_key_pem.encode(),
   password=None,
   backend=default_backend()
)

guardflo_public = serialization.load_pem_public_key(
   public_key_pem.encode(),
   backend=default_backend()
)


# -----------------------------
# Sign decision
# -----------------------------

def sign_decision(payload: dict) -> str:

   message = json.dumps(payload, sort_keys=True, default=str).encode()

   signature = guardflo_private.sign(
       message,
       padding.PSS(
           mgf=padding.MGF1(hashes.SHA256()),
           salt_length=padding.PSS.MAX_LENGTH
       ),
       hashes.SHA256()
   )

   return base64.b64encode(signature).decode()


# -----------------------------
# Verify signature
# -----------------------------

def verify_signature(payload: dict, signature: str) -> bool:

   message = json.dumps(payload, sort_keys=True, default=str).encode()

   signature_bytes = base64.b64decode(signature)

   try:

       guardflo_public.verify(
           signature_bytes,
           message,
           padding.PSS(
               mgf=padding.MGF1(hashes.SHA256()),
               salt_length=padding.PSS.MAX_LENGTH
           ),
           hashes.SHA256()
       )

       return True

   except Exception:
       return False