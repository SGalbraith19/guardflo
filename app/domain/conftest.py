import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



@pytest.fixture
def db_session():
   
   engine = create_engine("sqlite:///:memory:", echo=False)

  

   SessionLocal = sessionmaker(bind=engine)
   session = SessionLocal()

   try:
       yield session
   finally:
       session.close()