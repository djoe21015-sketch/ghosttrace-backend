from fastapi import APIRouter, WebSocket
from app.services.scan_service import run_scan
from app.database import SessionLocal
from app.models.target import Target

router = APIRouter()

@router.websocket("/ws/scan/{target_id}")
async def websocket_scan(websocket: WebSocket, target_id: int):
    await websocket.accept()

    db = SessionLocal()
    target = db.query(Target).filter(Target.id == target_id).first()

    if not target:
        await websocket.send_text("ERROR: Target not found.")
        await websocket.close()
        return

    await websocket.send_text("Starting scan...")

    # Run scan
    result = run_scan(target)

    await websocket.send_text("Scan complete.")
    await websocket.send_text("Preparing report...")

    # Send final report text
    await websocket.send_text(result["report_text"])

    await websocket.send_text("DONE")
    await websocket.close()
