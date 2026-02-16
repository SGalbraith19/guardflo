# ai_service/explainer.py

def explain_event(event: dict) -> dict:
   event_type = event.get("event_type")

   if event_type == "booking.status_changed":
       return {
           "summary": (
               f"Booking {event['payload']['booking_id']} "
               f"changed from {event['payload']['old_status']} "
               f"to {event['payload']['new_status']}."
           ),
           "confidence": 0.99,
           "explanation": (
               "This change occurred because the requested lifecycle "
               "transition was valid under the configured rules."
           ),
       }

   if event_type == "capacity.limit_reached":
       return {
           "summary": "Capacity constraint triggered.",
           "confidence": 0.95,
           "explanation": (
               "The operation was blocked because allowing it would "
               "have exceeded a configured capacity limit."
           ),
       }

   return {
       "summary": "Unrecognized event.",
       "confidence": 0.50,
       "explanation": "No explanation available.",
   }