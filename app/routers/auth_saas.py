from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import psycopg2

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

def pg_connect():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="yourpassword",
        database="ghosttrace"
    )

class RegisterModel(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(password):
    return pwd_context.hash(password)

@router.post("/register")
def register(user: RegisterModel):
    conn = pg_connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=%s", (user.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)

    cur.execute("""
        INSERT INTO users (email, password_hash, subscription_status)
        VALUES (%s, %s, %s)
    """, (user.email, hashed, "inactive"))

    conn.commit()
    conn.close()

    return {"message": "User registered successfully"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = pg_connect()
    cur = conn.cursor()

    cur.execute("SELECT id, password_hash FROM users WHERE email=%s", (form_data.username,))
    row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user_id, password_hash = row

    if not verify_password(form_data.password, password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": str(user_id)})

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
