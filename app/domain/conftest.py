import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base


@pytest.fixture
def db_session():
   
   engine = create_engine("sqlite:///:memory:", echo=False)

   Base.metadata.create_all(engine)

   SessionLocal = sessionmaker(bind=engine)
   session = SessionLocal()

   try:
       yield session
   finally:
       session.close()