import ipaddress
from queue import Queue
from threading import Thread
from typing import Iterator, Union
import socket

from .protocol import NetworkProtocolException

from .client import Client

def ping_box(address: str, port: int) -> Union[Client, None]:
    try:
        client = Client(address, port)
        client.start()
        client.close()
        return Client(address, port)
    except (socket.error, NetworkProtocolException):
        return None

def get_available_boxes(interface: str, port: int) -> Iterator[Client]:
    network = ipaddress.ip_interface(interface).network
    total = 0
    queue = Queue()
    for host in network.hosts():
        addr = str(host)
        Thread(target=lambda: queue.put(ping_box(addr, port)), daemon=True).start()
        total += 1
    while total > 0:
        if client := queue.get():
            yield client
        total -= 1