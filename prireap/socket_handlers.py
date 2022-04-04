from .socket_manager import SocketManager

sio=SocketManager()


#ws://127.0.0.1:8000/ws/socket.io/
# function put at here is not work at all

@sio.event
async def connect(sid, environ):
    print("server been connected with client sid:{} \n".format(sid))
    #don't emit any message immediately here.
    # await sio.sleep(1.0)
    # await sio.emit(event='my_message',data={'dict':1}) #don't emit immediatly, client can't hold

# @sio.event
# async def message(sid, data):
#     print('message,sid:{},data:{}'.format(sid,data))

@sio.event
async def pub_kday(sid, data):
    '''
    TODO
    * 到處都是room name，很亂又沒有auto complete
    '''
    await sio.emit('kday',data,room='kday_sub_gp')
    # print("in pub kday:",data)

@sio.on('sub_kday')
async def sub_kday(sid):
    '''
    * when client want to subscribe specific data. need to call the endpoint to regist
    * self.server.manager.rooms.keys()
    '''
    sio.enter_room(sid=sid, room='kday_sub_gp')
    print('sid:{} enter room:{}\n'.format(sid,'kday_sub_gp'))

@sio.on('unsub_kday')
async def exit_chat(sid):
    sio.leave_room(sid, 'kday_sub_gp')
    print('sid:{} leave room:{}\n'.format(sid,'kday_sub_gp'))


# @sio.on('*')
# async def catch_all(event, sid, data):
#     print('this is all:', event, sid, data)
    # pass

@sio.event
async def join(sid, data):
    print('this is join ', sid, data)
    await sio.emit(event='sub_kday',data={'dict':1})

# @sio.on('leave')
# async def handle_leave(sid, *args, **kwargs):
#     await sio.emit('lobby', 'User left')




