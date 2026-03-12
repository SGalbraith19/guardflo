import hashlib
from typing import List


def hash_pair(a: str, b: str) -> str:
   return hashlib.sha256((a + b).encode()).hexdigest()


def compute_merkle_root(hashes: List[str]) -> str:
   if not hashes:
       return ""

   layer = hashes[:]

   while len(layer) > 1:
       if len(layer) % 2 == 1:
           layer.append(layer[-1])

       new_layer = []

       for i in range(0, len(layer), 2):
           new_layer.append(hash_pair(layer[i], layer[i + 1]))

       layer = new_layer

   return layer[0]