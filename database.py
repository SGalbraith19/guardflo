import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tenancy.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL:", DATABASE_URL)  # ← PUT IT HERE

if not DATABASE_URL:
   raise RuntimeError("DATABASE_URL environment variable not set")

engine = create_engine(
   DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
   connect_args={"sslmode": "require"},
)

SessionLocal = sessionmaker(
   autocommit=False,
   autoflush=False,
   bind=engine,
)

Base.metadata.create_all(bind=engine)