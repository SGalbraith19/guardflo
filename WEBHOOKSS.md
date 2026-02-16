# Webhooks

Tradie Scheduler sends HTTP POST webhooks when important events occur.

---

## Events

### booking.status_changed

Triggered whenever a booking status changes.

---

## Payload

```json
{
 "booking_id": "123",
 "old_status": "scheduled",
 "new_status": "completed"
}