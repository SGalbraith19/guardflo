from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class AIEvent(Base):
   __tablename__ = "ai_events"

   id = Column(Integer, primary_key=True)
   ...