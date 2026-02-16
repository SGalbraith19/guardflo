import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from support_ai.models import Base

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
   raise RuntimeError("DATABASE_URL environment variable not set")

engine = create_engine(
   DATABASE_URL,
   connect_args={"sslmode": "require"}
)

# Create tables automatically
Base.metadata.create_all(bind=engine)