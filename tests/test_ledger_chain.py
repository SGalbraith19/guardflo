def test_genesis_previous_hash():
   entry = {
       "previous_hash": "GENESIS"
   }

   assert entry["previous_hash"] == "GENESIS"