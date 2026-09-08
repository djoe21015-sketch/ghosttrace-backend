from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/updates")
async def websocket_updates(ws: WebSocket):
    await ws.accept()
    await ws.send_text("Connected to GhostTrace WebSocket")

    # Placeholder loop — later scrapers will push real updates
    while True:
        await ws.send_text("heartbeat")
        await ws.receive_text()  # keeps connection alive
