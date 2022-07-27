import math
import socket as sck
from types import FunctionType

def read_socket(socket: sck.socket, action: FunctionType):
    exp = socket.recv(1)[0]
    message = socket.recv(2**exp)
    action(message)

def write_socket(socket: sck.socket, data: bytes):
    exp = int(math.log2(len(data)))+1
    socket.sendall(bytearray([exp]))
    socket.sendall(data)