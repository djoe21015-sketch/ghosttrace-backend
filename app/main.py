from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, targets, reports, status
from app.routers import auth_saas
from app.routers import osint
from app.sockets.updates import router as ws_router

from app.database import init_db, get_db
from app.models import User
from sqlalchemy.orm import Session

import stripe
from app.config import STRIPE_SECRET_KEY

app = FastAPI(title="GhostTrace OSINT Engine")

# Allow dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# REST API routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(targets.router, prefix="/targets", tags=["targets"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(osint.router, tags=["osint"])
app.include_router(auth_saas.router, prefix="/saas/auth", tags=["saas-auth"])

# WebSocket routes
app.include_router(ws_router, prefix="/ws")

@app.get("/")
def root():
    return {"GhostTrace": "OSINT Engine Online"}


# ⭐ STRIPE CHECKOUT ROUTE — THIS MAKES YOU MONEY
stripe.api_key = STRIPE_SECRET_KEY

@app.post("/create-checkout-session")
async def create_checkout_session(plan_id: str):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": plan_id,
                "quantity": 1
            }],
            success_url="https://ghosttrace.io/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://ghosttrace.io/cancel"
        )
        return {"checkout_url": session.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ⭐ DASHBOARD LOCKING — REQUIRE PLAN
def require_plan(required_plan):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            db = next(get_db())
            user_id = kwargs.get("user_id")

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if user.subscription_plan != required_plan:
                raise HTTPException(status_code=403, detail="Upgrade required")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ⭐ STORE SUBSCRIPTION IN DATABASE
@app.post("/store-subscription")
async def store_subscription(session_id: str, user_id: int, db: Session = Depends(get_db)):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        subscription = stripe.Subscription.retrieve(session.subscription)

        plan_id = subscription.items.data[0].price.id
        status = subscription.status
        customer_id = subscription.customer

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.subscription_plan = plan_id
        user.subscription_status = status
        user.stripe_customer_id = customer_id

        db.commit()

        return {
            "message": "Subscription stored",
            "plan": plan_id,
            "status": status
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ⭐ CHECK SUBSCRIPTION STATUS
@app.get("/subscription-status")
async def subscription_status(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        subscription = stripe.Subscription.retrieve(session.subscription)

        return {
            "status": subscription.status,
            "plan_id": subscription.items.data[0].price.id,
            "customer_id": subscription.customer
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
