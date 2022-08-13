from typing import NewType, Tuple
import math
import socket as sck

class NetworkProtocolException(Exception): pass

ActionCode = NewType('ActionCode', int)

PROT_ACTION_APP:    ActionCode = 0
PROT_ACTION_NOTIFY: ActionCode = 1
PROT_ACTION_PING:   ActionCode = 2
PROT_ACTION_LOGIN:  ActionCode = 3
PROT_ACTION_FOUND:  ActionCode = 4
PROT_ACTION_GRANT:  ActionCode = 5
PROT_ACTION_DENIE:  ActionCode = 6

def read_socket(socket: sck.socket) -> Tuple[ActionCode, bytes]:
    action, length = split_status(socket.recv(1)[0])
    message = socket.recv(length)
    return action, message

def write_socket(socket: sck.socket, action: ActionCode, data: bytes):
    socket.sendall(bytearray([get_status(action, len(data))]))
    socket.sendall(data)

def split_status(status: int) -> Tuple[ActionCode, int]:
    return status & 15, 2**(status >> 4)

def get_status(action: ActionCode, length: int) -> int:
    exp = int(math.log2(length))+1
    return (exp << 4) + action