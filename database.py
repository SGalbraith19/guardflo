import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# ---- DATABASE URL ----
DATABASE_URL = os.getenv(
   "DATABASE_URL",
   "postgresql://postgres:postgres@localhost:5432/tradie_scheduler"
)

# ---- ENGINE ----
engine = create_engine(
   DATABASE_URL,
   pool_pre_ping=True,
   future=True,
)

# ---- SESSION FACTORY ----
SessionLocal = sessionmaker(
   bind=engine,
   autocommit=False,
   autoflush=False,
   expire_on_commit=False,
)

# ---- BASE MODEL ----
Base = declarative_base()


# ---- DEPENDENCY INJECTION ----
def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()