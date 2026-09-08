import os
import sqlite3
import stripe
import jwt
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel

# ENGINE IMPORT
from app.engine.engine import run_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "ghosttrace.db")

STRIPE_SECRET_KEY = "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"
STRIPE_PUBLISHABLE_KEY = "pk_live_51U8zxGQcBIIZXfeMvmEswgcRNiVGD8lV3aVeES7YYh29DxVwC0AXbrhiW4R2ojYeSymDMBAeOOocubNUWn2CZUzC00fYPmTBWv"

PRICE_BASIC_MONTHLY = "price_1U92s8QcBIIZXfeMWboTdXjL"
PRICE_PRO_MONTHLY   = "price_1U9JkZQcBIIZXfeMjwDT1meU"
PRICE_ULTRA_MONTHLY = "price_1U9JmyQcBIIZXfeMcyR9azlP"
PRICE_ENTERPRISE    = "price_1U9L1PQcBIIZXfeMcvoIvK7w"

JWT_SECRET = "ghosttrace_secret_key"
JWT_ALGORITHM = "HS256"

stripe.api_key = STRIPE_SECRET_KEY

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            plan_id TEXT DEFAULT 'free'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, email, plan_id FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="User not found")

    return {"id": row["id"], "email": row["email"], "plan_id": row["plan_id"]}

def require_plan(user, allowed_plans):
    if user["plan_id"] not in allowed_plans:
        raise HTTPException(status_code=403, detail="Upgrade required")

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class CheckoutRequest(BaseModel):
    plan_id: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register(data: RegisterRequest):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (data.email, data.password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    conn.close()
    return {"status": "ok"}

@app.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE email = ?", (data.email,))
    row = c.fetchone()
    conn.close()

    if not row or row["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"user_id": row["id"]}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"token": token}

@app.get("/me")
def me(user=Depends(get_current_user)):
    return {"email": user["email"], "plan_id": user["plan_id"]}

@app.post("/create-checkout-session")
def create_checkout_session(data: CheckoutRequest, user=Depends(get_current_user)):
    price_id = data.plan_id
    if not price_id:
        raise HTTPException(status_code=400, detail="Missing plan_id")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        customer_email=user["email"],
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="https://ghosttrace.io/success",
        cancel_url="https://ghosttrace.io/cancel"
    )

    return {"checkout_url": session.url}

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, "whsec_REPLACE_WITH_YOUR_WEBHOOK_SECRET"
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "customer.subscription.updated":
        sub = event["data"]["object"]
        email = sub["customer_email"]
        plan = sub["items"]["data"][0]["price"]["id"]

        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET plan_id = ? WHERE email = ?", (plan, email))
        conn.commit()
        conn.close()

    return {"status": "ok"}

@app.post("/run-scan")
def run_scan(target: str, user=Depends(get_current_user)):
    require_plan(user, [
        PRICE_BASIC_MONTHLY,
        PRICE_PRO_MONTHLY,
        PRICE_ULTRA_MONTHLY,
        PRICE_ENTERPRISE
    ])
    return run_engine(target)

@app.get("/")
def home():
    return {"status": "GhostTrace API running"}
