from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Organisation(Base):
   __tablename__ = "organisation"

   org_id = Column(String, primary_key=True)
   org_name = Column(String, nullable=False)
   tier = Column(String, nullable=False)  # small | medium | large
   api_key = Column(String, unique=True, nullable=False)
   active = Column(Boolean, default=True)

subscription_active = Column(Boolean, default=False)
tier = Column(String, default="free")