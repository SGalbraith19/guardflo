import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from rsa import PublicKey

# Load private key
with open("private_key.pem", "rb") as f:
   guardflo_private = serialization.load_pem_private_key(
       f.read(),
       password=None,
       backend=default_backend()
   )

# Load public key
with open("public_key.pem", "rb") as f:
   guardflo_public = serialization.load_pem_public_key(
       f.read(),
       backend=default_backend()
   )


def sign_decision(payload: dict) -> str:
   message = json.dumps(payload, sort_keys=True, default=str).encode()

   signature = guardflo_private.sign(
       message,
       padding.PSS(
           mgf=padding.MGF1(hashes.SHA256()),
           salt_length=padding.PSS.MAX_LENGTH,
       ),
       hashes.SHA256(),
   )

   return base64.b64encode(signature).decode()


def verify_signature(payload: dict, signature: str) -> bool:
   message = json.dumps(payload, sort_keys=True, default=str).encode()
   signature_bytes = base64.b64decode(signature)

   try:
       PublicKey.verify(
           signature_bytes,
           message,
           padding.PSS(
               mgf=padding.MGF1(hashes.SHA256()),
               salt_length=padding.PSS.MAX_LENGTH,
           ),
           hashes.SHA256(),
       )
       return True
   except Exception:
       return False