from socket import gethostbyname
from queue import Queue

from .client import Client
from .server import Server

def test_messages():
    active_clients = []
    servermsg = Queue()
    clientmsg = Queue()

    s = Server(gethostbyname('localhost'), 9591)
    s.on_connect(lambda id: active_clients.append(id))
    s.start(lambda _, data: servermsg.put(data))

    c = Client(gethostbyname('localhost'), 9591)
    c.start(lambda data: clientmsg.put(data))

    clientdata = b'Sent by client'
    c.emit(clientdata)
    assert servermsg.get() == clientdata

    serverdata = b'Sent by server'
    s.emit(active_clients[0], serverdata)
    assert clientmsg.get() == serverdata

    s.close()
    c.close()