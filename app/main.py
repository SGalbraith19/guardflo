from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date, time
from typing import List
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
import uuid
import secrets
from app.models import Booking, User, WebhookSubscription

from app.database import SessionLocal
from app.domain.bookings import update_booking_status
from app.webhooks.webhook_dispatcher import dispatch_webhook
from app.webhooks.webhook_events import BOOKING_STATUS_CHANGED
from app.domain.status_validation import validate_status_transition

app = FastAPI()

import uuid

from app.database import SessionLocal

from pydantic import BaseModel
import secrets

class WebhookCreate(BaseModel):
    target_url: str
    event: str


pwd_context = CryptContext(
   schemes=["bcrypt"],
   deprecated="auto"
)
SECRET_KEY = "change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKENS_EXPIRE_DAYS = 7
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from app.database import SessionLocal

def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()

def hash_password(password: str) -> str:
   return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
   return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_refresh_token(user_id: str):
   expire = datetime.utcnow() + timedelta(days=REFRESH_TOKENS_EXPIRE_DAYS)
   payload = {
       "sub": user_id,
       "exp": expire,
       "type": "refresh"
   }

def get_current_user(
   token: str = Depends(oauth2_scheme),
   db: Session = Depends(get_db),
):
   credentials_exception = HTTPException(
       status_code=status.HTTP_401_UNAUTHORIZED,
       detail="Could not validate credentials",
       headers={"WWW-Authenticate": "Bearer"},
   )

   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       user_id: str | None = payload.get("sub")
       if user_id is None:
           raise credentials_exception
   except JWTError:
       raise credentials_exception

   user = db.query(user).filter(user.id == user_id).first()
   if user is None:
       raise credentials_exception

   return user

def get_current_user(
   token: str = Depends(oauth2_scheme),
   db: Session = Depends(get_db),
):
   credentials_exception = HTTPException(
       status_code=status.HTTP_401_UNAUTHORIZED,
       detail="Could not validate credentials",
       headers={"WWW-Authenticate": "Bearer"},
   )

   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       user_id: str | None = payload.get("sub")
       if user_id is None:
           raise credentials_exception
   except JWTError:
       raise credentials_exception

   user = db.query(user).filter(user.id == user_id).first()
   if user is None:
       raise credentials_exception

   return user

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
   token: str = Depends(oauth2_scheme),
   db: Session = Depends(get_db),
):
   
   credentials_exception = HTTPException(
       status_code=status.HTTP_401_UNAUTHORIZED,
       detail="Could not validate credentials",
       headers={"WWW-Authenticate": "Bearer"},
   )

   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       user_id: str | None = payload.get("sub")
       if user_id is None:
           raise credentials_exception
   except JWTError:
       raise credentials_exception

   user = db.query(user).filter(user.id == user_id).first()
   if user is None:
       raise credentials_exception

   return user

def require_admin(current_user: User = Depends(get_current_user)):
   if current_user.role != "admin":
       raise HTTPException(status_code=403, detail="Admin access required")
   return current_user


class UserCreate(BaseModel):
   email: str
   name: str

class BookingCreate(BaseModel):
    job_type: str
    job_date: str
    job_time: str
    notes: str | None = None

STATUS_TRANSITIONS = {
    "scheduled": ["confirmed", "cancelled"],
    "confirmed": ["cancelled"],
    "cancelled": []
}
def is_valid_staus_transition(current_status: str, new_status: str) -> bool:
    allowed = STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed

def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()

@app.get("/")
def home():
   return {"message": "Tradie Scheduler is running"}

@app.get("/bookings")
def list_bookings(
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   bookings = (
       db.query(Booking)
       .filter(Booking.user_id == current_user.id)
       .all()
   )
   return (
       db.query(Booking)
       .filter(Booking.user_id == current_user.id)
       .all()
   )

@app.post("/bookings")
def create_booking(
   booking: BookingCreate,
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   new_booking = Booking(
       job_type=booking.job_type,
       job_date=booking.job_date,
       job_time=booking.job_time,
       notes=booking.notes,
       user_id=current_user.id,
   )

   db.add(new_booking)
   db.commit()
   db.refresh(new_booking)
   return new_booking

@app.delete("/bookings/{booking_id}")
def delete_booking(
   booking_id: str,
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   booking = db.query(Booking).filter(
       Booking.id == booking_id,
       Booking.user_id == current_user.id,
   ).first()

   if not booking:
       raise HTTPException(status_code=404, detail="Booking not found")

   db.delete(booking)
   db.commit()
   return {"detail": "Booking deleted"}

@app.patch("/bookings/{booking_id}/status")
def update_booking_status(
   booking_id: str,
   status: str,
   db: Session = Depends(get_db),
):
   booking = db.query(Booking).filter(Booking.id == booking_id).first()

   if not booking:
       raise HTTPException(status_code=404, detail="Booking not found")

   if status not in ["scheduled", "completed", "cancelled"]:
       raise HTTPException(
           status_code=400,
           detail="Invalid status. Use scheduled, completed, or cancelled",
       )

@app.post("/users")
def create_user(
   email: str,
   name: str,
   password:str,
   db: Session = Depends(get_db),
):
   hashed_password = pwd_context.hash(password)

   user = User(
      email=email,
      name=name,
      password_hash=hash_password(password),
   )
   db.add(user)
   db.commit()
   db.refresh(user)

   return {
       "id": user.id,
       "email": user.email,
       "name": user.name,
   }

@app.get("/bookings")
def list_bookings(
   limit: int = 20,
   offset: int = 0,
   db: Session = Depends(get_db),
   current_user: User = Depends(get_current_user),
):
   return (
       db.query(Booking)
       .filter(Booking.user_id == current_user.id)
       .limit(limit)
       .offset(offset)
       .all()
   )

@app.post("/bookings")
def create_booking(
   booking: BookingCreate,
   db: Session = Depends(get_db),
   current_user: User = Depends(get_current_user),
):
   new_booking = Booking(
       id=str(uuid.uuid4()),
       job_type=booking.job_type,
       job_date=booking.job_date,
       job_time=booking.job_time,
       notes=booking.notes,
       status="pending",
       user_id=current_user.id, 
   )
   db.add(new_booking)
   db.commit()
   db.refresh(new_booking)
   return new_booking

@app.delete("/bookings/{booking_id}")
def delete_booking(
   booking_id: str,
   db: Session = Depends(get_db),
   current_user: User = Depends(get_current_user),
):
   booking = db.query(Booking).filter(
       Booking.id == booking_id,
       Booking.user_id == current_user.id
   ).first()

   if not booking:
       raise HTTPException(status_code=404, detail="Booking not found")

   db.delete(booking)
   db.commit()
   return {"message": "Booking deleted"}

@app.patch("/bookings/{booking_id}/status")
def update_booking_status_route(
   booking_id: str,
   status: str,
   db: Session = Depends(get_db),
):
   booking = db.query(Booking).filter(Booking.id == booking_id).first()

   if not booking:
       raise HTTPException(status_code=404, detail="Booking not found")

   booking = update_booking_status(
       db=db,
       booking=booking,
       new_status=status,
   )

   return {
       "id": booking.id,
       "status": booking.status,
   }

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def login(
   form_data: OAuth2PasswordRequestForm = Depends(),
   db: Session = Depends(get_db),
):
   user = db.query(User).filter(User.email == form_data.username).first()

   if not user:
       raise HTTPException(status_code=401, detail="Invalid credentials")

   if not verify_password(form_data.password, user.password_hash):
       raise HTTPException(status_code=401, detail="Invalid credentials")

   access_token = create_access_token(
       data={"sub": user.id}
   )

   return {
       "access_token": access_token,
       "refresh_token": create_refresh_token(user.id),
       "token_type": "bearer",
   }

@app.get("/admin/users")
def list_all_users(
   db: Session = Depends(get_db),
   admin: User = Depends(require_admin),
):
    return db.query(User).all()

@app.post("/refresh")
def refresh_access_token(token: str = Depends(oauth2_scheme)):
   try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       if payload.get("type") != "refresh":
           raise HTTPException(status_code=401)

       return {
           "access_token": create_access_token({"sub": payload["sub"]})
       }
   except JWTError:
       raise HTTPException(status_code=401)
   
@app.post("/webhooks")
def create_webhook(
   webhook: WebhookCreate,
   db: Session = Depends(get_db)
):
   secret = secrets.token_hex(32)

   record = WebhookSubscription(
       target_url=webhook.target_url,
       event=webhook.event,
       secret=secret
   )

   db.add(record)
   db.commit()

   return {
       "id": str(record.id),
       "secret": secret
   }

@app.post("/webhooks/test")
def test_webhook(payload: dict, request: Request):
   signature = request.headers.get("X-Signature")
   return {
       "received": True,
       "signature": signature,
       "payload": payload
   }