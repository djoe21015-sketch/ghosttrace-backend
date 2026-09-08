from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid

from app.database import SessionLocal
from app.models.user import User

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register new user
@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = pwd.hash(password)
    api_key = str(uuid.uuid4())

    user = User(email=email, password_hash=hashed, api_key=api_key)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered", "api_key": api_key}

# Login
@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not pwd.verify(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful", "api_key": user.api_key}
