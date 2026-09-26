import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()
NAME = os.environ.get("INSTANCE", "unknown")


@app.get("/healthz")
def healthz():
    return {"ok": True, "instance": NAME}


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(f"connected to {NAME}")
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(f"[{NAME}] echo: {msg}")
    except WebSocketDisconnect:
        pass
