def fifo_priority(metadata: dict) -> int:

   if "priority" in metadata:
       return int(metadata["priority"])

   start_date = metadata.get("start_date")
   created_at = metadata.get("created_at")

   if start_date:
       return int(start_date.replace("-", ""))

   return int(created_at.timestamp())