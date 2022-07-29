from dataclasses import dataclass
import socket as sck
from socket import socket
from threading import Thread
from types import FunctionType
from typing import Iterator, List, Tuple

from .utils import read_socket, write_socket

ClientId = Tuple[int, int]

@dataclass
class StoredClient:
    """Connected client representation inside the server"""
    client: socket
    addr: str
    thread: Thread
    pos: int

    def __hash__(self) -> int:
        return hash((self.addr, self.pos))

    def id(self) -> ClientId:
        return (self.pos, hash(self))

class Server:
    """
    The Server is an object that awaits Clients to get connected in order to offer them services
    """

    def __init__(self, addr: str, port: int, family: sck.AddressFamily = sck.AF_INET) -> None:
        self.socket: socket = socket(family, sck.SOCK_STREAM)
        self.socket.bind((addr, port))
        self.mainloop: Thread = None
        self.running: bool = False

        self.clients: List[StoredClient] = []
        
        self.mailbox: FunctionType = None
        self.on_connect_callback: FunctionType = None

    def start(self, mailbox: FunctionType, daemon=True, backlog=5):
        self.mailbox = mailbox
        
        self.socket.listen(backlog)
        self.running = True
        self.mainloop = Thread(target=self.__mainloop, daemon=daemon)
        self.mainloop.start()

    def on_connect(self, callback: FunctionType):
        self.on_connect_callback = callback

    def __mainloop(self):
        while self.running:
            #Client information and future position
            client, addr = self.socket.accept()
            pos, append = self.__find_empty()
            #Thread and client creation
            args = [None]
            thread = Thread(target=self.__handle_client, args=args)
            client = StoredClient(client, str(addr), thread, pos)
            args[0] = client
            #Client store
            if append: self.clients.append(client)
            else: self.clients[pos] = client
            #Client actions, thread and connection notification
            self.on_connect_callback(client.id())
            thread.start()

    def __find_empty(self) -> Tuple[int, bool]:
        for p, i in enumerate(self.clients):
            if i == None: return p, False
        return len(self.clients), True

    def __handle_client(self, client: StoredClient):
        while self.running:
            read_socket(client.client, lambda msg: self.mailbox(client.id(), msg))

    def close(self):
        self.running = False
        self.socket.close()

    def emit(self, id: ClientId, data: bytes):
        client_info = self.clients[id[0]]
        if client_info:
            if id == client_info.id():
                write_socket(client_info.client, data)
    
    def who(self, id: ClientId):
        client_info = self.clients[id[0]]
        if client_info:
            if id == client_info.id():
                return client_info.addr
        return None

    def clients(self) -> Iterator[StoredClient]:
        for client in self.clients:
            if client: yield client