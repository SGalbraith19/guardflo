# app/domain/webhook_events.py

# Booking lifecycle events
BOOKING_CREATED = "booking.created"
BOOKING_UPDATED = "booking.updated"
BOOKING_STATUS_CHANGED = "booking.status_changed"

# Future-proofing (do not implement yet)
CAPACITY_EXCEEDED = "capacity.exceeded"
FIFO_REORDERED = "fifo.reordered"
SAFETY_VIOLATION_DETECTED = "safety.violation_detected"