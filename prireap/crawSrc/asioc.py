#async socketio client
import socketio
import asyncio

# sio = socketio.Client()
sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("I'm (client) connected!")
    # await sio.emit('join',{'foo': 'bar'})
    # await sio.emit('pub_kday',data={'test':123})



@sio.on('kday')
async def kday(data):
    print('kday:{}'.format(data))

@sio.event
async def my_message(data):
    print('I received a message!, data:{}'.format(data))
    
    await sio.emit('join',{'in my message': 'bar'})

@sio.event
def disconnect():
    print("I'm (client) disconnected!")

