import socketio
from typing import Optional, Union
from fastapi import FastAPI
from typing import Optional

'''
socket manager 不應該包住 fastapi app，而是fastapi 去包 socket manager
'''
class SocketManager:
    """
    Integrates SocketIO with FastAPI app. 
    Adds `sio` property to FastAPI object (app).

    Default mount location for SocketIO app is at `/ws`
    and defautl SocketIO path is `socket.io`.
    (e.g. full path: `ws://www.example.com/ws/socket.io/)

    SocketManager exposes basic underlying SocketIO functionality

    e.g. emit, on, send, call, etc.
    """

    def __init__(
        self,
        app: Optional[FastAPI]=None,
        mount_location: str = "/ws",
        socketio_path: str = "socket.io",
        cors_allowed_origins: Union[str, list] = '*',
        async_mode: str = "asgi"
    ) -> None:
        # TODO: Change Cors policy based on fastapi cors Middleware
        self._sio = socketio.AsyncServer(async_mode=async_mode, cors_allowed_origins=cors_allowed_origins)
        self._app = socketio.ASGIApp(
            socketio_server=self._sio, socketio_path=socketio_path
        )
        self.mount_location=mount_location

        if app!=None:
            app.mount(mount_location, self._app)
            app.sio = self._sio

    def be_mount(self, app:FastAPI):
        '''
        this function actually better be done by fastapi app itself.
        '''
        app.mount(self.mount_location, self._app)
        app.sio = self._sio
        

    def is_asyncio_based(self) -> bool:
        return True

    @property
    def event(self):
        return self._sio.event

    @property
    def on(self):
        return self._sio.on

    @property
    def attach(self):
        return self._sio.attach

    @property
    def emit(self):
        return self._sio.emit

    @property
    def send(self):
        return self._sio.send

    @property
    def call(self):
        return self._sio.call

    @property
    def close_room(self):
        return self._sio.close_room

    @property
    def get_session(self):
        return self._sio.get_session

    @property
    def save_session(self):
        return self._sio.save_session

    @property
    def session(self):
        return self._sio.session

    @property
    def disconnect(self):
        return self._sio.disconnect

    @property
    def handle_request(self):
        return self._sio.handle_request

    @property
    def start_background_task(self):
        return self._sio.start_background_task

    @property
    def sleep(self):
        return self._sio.sleep

    # @property #origianl wrong this is not property
    def enter_room(self, sid: str, room: str, namespace: Optional[str] = None):
        return self._sio.enter_room(sid, room, namespace)

    # @property
    def leave_room(self, sid: str, room: str, namespace: Optional[str] = None):
        return self._sio.leave_room(sid, room, namespace)

