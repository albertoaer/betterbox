from dataclasses import dataclass
import socket as sck
from socket import socket
from threading import Thread
from typing import Iterator, Union, Callable

from ..data_structures.reusable_list import MemberId, ReusableList
from .protocol import *

@dataclass
class StoredClient:
    """Connected client representation inside the server"""
    client: socket
    addr: str
    thread: Thread

    def __hash__(self) -> int:
        return hash(self.addr)

class Server:
    """
    The Server is an object that awaits Clients to get connected in order to offer them services
    """

    def __init__(self, addr: str, port: int, family: sck.AddressFamily = sck.AF_INET) -> None:
        self.socket: socket = socket(family, sck.SOCK_STREAM)
        self.socket.bind((addr, port))
        self.mainloop: Thread = None
        self.running: bool = False

        self.clients: ReusableList = ReusableList()
        
        self.mailbox: Callable = None
        self.on_connect_callback: Callable = None

    def start(self, mailbox: Callable=None, daemon=True, backlog=5):
        self.mailbox = mailbox
        
        self.socket.listen(backlog)
        self.running = True
        self.mainloop = Thread(target=self.__mainloop, daemon=daemon)
        self.mainloop.start()

    def on_connect(self, callback: Callable):
        self.on_connect_callback = callback

    def __mainloop(self):
        while self.running:
            try:
                #Client accept
                client, addr = self.socket.accept()
                #Thread and client creation
                idwrap = [None]
                thread = Thread(target=self.__handle_client, args=idwrap)
                idwrap[0] = self.clients.append(StoredClient(client, str(addr), thread))
                #Client actions, thread and connection notification
                self.on_connect_callback(idwrap[0])
                thread.start()
            except Exception as err:
                if self.running:
                    raise err

    def __handle_client(self, id: MemberId):
        try:
            while self.running and (client := self.clients[id]):
                action, msg = read_socket(client.client)
                if self.mailbox:
                    self.mailbox(id, msg)
        except Exception as err:
            #TODO: Log err
            self.clients.remove(id)

    def close(self):
        self.running = False
        self.socket.close()

    def emit(self, id: MemberId, data: bytes):
        if client := self.clients[id]:
            write_socket(client.client, PROT_ACTION_APP, data)
    
    def who(self, id: MemberId) -> Union[None, str]:
        if client := self.clients[id]:
            return client.addr
        return None

    def clients(self) -> Iterator[StoredClient]:
        for client in self.clients.collection:
            if client: yield client