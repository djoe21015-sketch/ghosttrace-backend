from fastapi import APIRouter
import time

router = APIRouter()

START_TIME = time.time()

@router.get("/health")
def health_check():
    return {"status": "online"}

@router.get("/version")
def version():
    return {"GhostTrace": "v1.0"}

@router.get("/uptime")
def uptime():
    return {"uptime_seconds": round(time.time() - START_TIME, 2)}
