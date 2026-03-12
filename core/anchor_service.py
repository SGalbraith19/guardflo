import requests

def anchor_merkle_root(root):
   requests.post(
       "https://anchor.guardflo.com",
       json={"merkle_root": root}
   )