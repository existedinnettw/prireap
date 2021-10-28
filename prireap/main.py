import uvicorn
# --------------
from typing import List
from sqlalchemy.orm import Session

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import HTMLResponse
from . import schemas, crud, models
from .database import SessionLocal, engine
from typing import List, Optional
import datetime
from .routers import exchanges, stocks, stockKMins, stockKHours

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
# ===================================================================================
app.include_router(exchanges.router)
app.include_router(stocks.router)
app.include_router(stockKMins.router)
app.include_router(stockKHours.router)


# @app.post("/kbars_hr")
# def get_kbas_hr(stks_qry:List[schemas.stockQuery], start:datetime.datetime, end:datetime.datetime):
#     return

# @app.websocket("/ws/stream_kbars_hr")
# async def stream_kbars_hr(ws:WebSocket, stks_qry:List[schemas.stockQuery]):
#     try:
#         while True:
#             pass
#     except WebSocketDisconnect:
#         pass

@app.post("/create_kbars_hr")
def create_kbars_hr(stk_k_hr_li: List[schemas.StockKBar]):
    return


@app.websocket("/ws/notify_kbars_hr")
async def notify_kbars_hr(ws: WebSocket):
    try:
        while True:
            pass
    except WebSocketDisconnect:
        pass


# ==========================================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                log_level="info", reload=True)
