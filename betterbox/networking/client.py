import socket as sck
from socket import socket
from threading import Thread
from types import FunctionType

from .utils import read_socket, write_socket

class Client:
    """
    A Client is an object that connect to server in order to get services from it
    """

    def __init__(self, addr: str, port: int, family: sck.AddressFamily = sck.AF_INET) -> None:
        self.client: socket = socket(family, sck.SOCK_STREAM)
        self.target: tuple = (addr, port)
        self.mainloop: Thread = None
        self.running: bool = False

        self.mailbox: FunctionType = None

    def start(self, mailbox: FunctionType, daemon=True):
        self.mailbox = mailbox

        self.client.connect(self.target)
        self.mainloop = Thread(target=self.__mainloop, daemon=daemon)
        self.running = True
        self.mainloop.start()

    def __mainloop(self):
        while self.running:
            read_socket(self.client, lambda msg: self.mailbox(msg))

    def close(self):
        self.client.close

    def emit(self, data: bytes):
        write_socket(self.client, data)