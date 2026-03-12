import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import event
from sqlalchemy import String

from database import Base


class FinancialLedger(Base):
   __tablename__ = "financial_ledger"

   # Primary ID
   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

   # Tenant / Organisation link
   organisation_id = Column(
       UUID(as_uuid=True),
       ForeignKey("organisations.id", ondelete="CASCADE"),
       nullable=False
   )

   organisation = relationship("Organisation")

   # Decision metadata
   policy_version = Column(String, nullable=False)
   engine_version = Column(String, nullable=False)

   # Decision outcome
   decision = Column(Boolean, nullable=False)

   # Request fingerprint
   request_hash = Column(String, nullable=False)

   # Ledger hash chain
   previous_hash = Column(String, nullable=True)
   entry_hash = Column(String, nullable=False)

   # Cryptographic signature
   signature = Column(Text, nullable=False)

   # Request safety
   idempotency_key = Column(String, unique=True, index=True)
   nonce = Column(String(64), nullable=False, index=True)

   merkle_root = Column(String)

   # Timestamp
   created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Prevent updates (ledger is immutable)
@event.listens_for(FinancialLedger, "before_update")
def prevent_ledger_update(mapper, connection, target):
   raise Exception("Ledger entries are immutable")