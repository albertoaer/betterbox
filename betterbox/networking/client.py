import socket as sck
from socket import socket
from threading import Thread
from typing import Callable

from .protocol import *

CLIENT_TIMEOUT: float = 2

class Client:
    """
    A Client is an object that connect to server in order to get services from it
    """

    def __init__(self, addr: str, port: int, family: sck.AddressFamily = sck.AF_INET) -> None:
        self.client: socket = socket(family, sck.SOCK_STREAM)
        self.client.settimeout(CLIENT_TIMEOUT)
        self.target: tuple = (addr, port)
        self.mainloop: Thread = None
        self.running: bool = False

        self.mailbox: Callable = None

    def start(self, mailbox: Callable=None, daemon=True):
        self.mailbox = mailbox

        self.client.connect(self.target)
        self.mainloop = Thread(target=self.__mainloop, daemon=daemon)
        self.running = True
        self.mainloop.start()

    def __mainloop(self):
        while self.running:
            action, msg = read_socket(self.client)
            if self.mailbox:
                self.mailbox(msg)

    def close(self):
        self.client.close

    def emit(self, data: bytes):
        write_socket(self.client, PROT_ACTION_APP, data)