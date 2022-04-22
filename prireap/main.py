from operator import eq
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
from .routers import exchanges, stocks, stockKBars, dvdSplt, cfs, cash_flow, eqtyDisp
# from fastapi_socketio import SocketManager
from .socket_handlers import sio

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
sio.be_mount(app=app)


# ===================================================================================
app.include_router(exchanges.router)
app.include_router(stocks.router)
app.include_router(stockKBars.router)
app.include_router(dvdSplt.router)
app.include_router(cfs.router)
app.include_router(cash_flow.router)
app.include_router(eqtyDisp.router)


# ==========================================================================
if __name__ == "__main__":
    #https://stackoverflow.com/questions/60819376/fastapi-throws-an-error-error-loading-asgi-app-could-not-import-module-api
    uvicorn.run("prireap.main:app", host="127.0.0.1", port=8000,
                log_level="info",
                reload=True
                )
