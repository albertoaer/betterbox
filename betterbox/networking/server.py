import socket as sck
from socket import socket
from threading import Thread
from types import FunctionType
from typing import Iterator, Tuple

from .utils import read_socket, write_socket

class Server:
    """
    The Server is an object that awaits Clients to get connected in order to offer them services
    """

    def __init__(self, addr: str, port: int, family: sck.AddressFamily = sck.AF_INET) -> None:
        self.socket: socket = socket(family, sck.SOCK_STREAM)
        self.socket.bind((addr, port))
        self.mainloop: Thread = None
        self.running: bool = False

        self.clients: list = []
        
        self.mailbox: FunctionType = None

    def start(self, mailbox: FunctionType, daemon=True, backlog=5):
        self.mailbox = mailbox
        
        self.socket.listen(backlog)
        self.running = True
        self.mainloop = Thread(target=self.__mainloop, daemon=daemon)
        self.mainloop.start()

    def __mainloop(self):
        while self.running:
            client, addr = self.socket.accept()
            pos, append = self.__find_empty()
            addrstr = str(addr)
            thread = Thread(target=self.__handle_client, args=(client, addrstr, pos))
            if append: self.clients.append((client, addrstr, thread))
            else: self.clients[pos] = (client, addrstr, thread)
            thread.start()

    def __find_empty(self) -> Tuple[int, bool]:
        for p, i in enumerate(self.clients):
            if i == None: return p, False
        return len(self.clients), True

    def __handle_client(self, client: socket, addr: str, pos: int):
        checksum = hash(addr)
        while self.running:
            read_socket(client, lambda msg: self.mailbox(pos, checksum, msg))

    def close(self):
        self.running = False
        self.socket.close()

    def emit(self, idx: int, checksum: int, data: bytes):
        client_info = self.clients[idx]
        if client_info:
            if hash(client_info[1]) == checksum:
                write_socket(client_info[0], data)

    def clients(self) -> Iterator[Tuple[socket, str, Thread]]:
        for client in self.clients:
            if client: yield client