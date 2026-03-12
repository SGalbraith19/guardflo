import hashlib
import requests

def anchor_merkle_root(root_hash: str):
   """
   Anchors merkle root externally.
   For now just logs it.
   Later can send to blockchain or timestamp service.
   """
   print(f"ANCHOR MERKLE ROOT: {root_hash}")