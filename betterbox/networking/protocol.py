from argparse import Action
from typing import Literal, NewType, Tuple
import socket as sck

PROT_SIZE_BYTES = 4
PROT_SIZE_BYTE_ORDER = 'little'

def max_value(): return (2 ** (8 * PROT_SIZE_BYTES)) - 1

def set_protocol_config(size_bytes: int = PROT_SIZE_BYTES, size_bytes_order: Literal['little', 'big'] = PROT_SIZE_BYTE_ORDER):
    if size_bytes < 1:
        raise ValueError('The number of bytes must be at least 1')
    if size_bytes_order not in ['little', 'big']:
        raise ValueError("The byte order must be either 'little' or 'big'")
    global PROT_SIZE_BYTES
    global PROT_SIZE_BYTE_ORDER
    PROT_SIZE_BYTES = size_bytes
    PROT_SIZE_BYTE_ORDER = size_bytes_order

class NetworkProtocolException(Exception): pass

ActionCode = NewType('ActionCode', int)

PROT_ACTION_APP:    ActionCode = 0
PROT_ACTION_NOTIFY: ActionCode = 1
PROT_ACTION_PING:   ActionCode = 2
PROT_ACTION_LOGIN:  ActionCode = 3
PROT_ACTION_FOUND:  ActionCode = 4
PROT_ACTION_GRANT:  ActionCode = 5
PROT_ACTION_DENIE:  ActionCode = 6

#The format will be [length of size PROT_SIZE_BYTES][1 byte action][... message determied by length]
#First part: [length of size PROT_SIZE_BYTES][1 byte action] is called header
#Last part: [... message determied by length] is called body

def write_socket(socket: sck.socket, action: ActionCode, data: bytes):
    socket.sendall(serialize_header(len(data), action) + data)

def serialize_header(length: int, action: ActionCode) -> bytes:
    return length.to_bytes(PROT_SIZE_BYTES, PROT_SIZE_BYTE_ORDER) + bytearray([action])

def read_socket(socket: sck.socket) -> Tuple[ActionCode, bytes]:
    header = socket.recv(PROT_SIZE_BYTES + 1)
    length, action = deserialize_header(header)
    data = socket.recv(length)
    return action, data

def deserialize_header(header: bytes) -> Tuple[int, Action]:
    return int.from_bytes(header[:PROT_SIZE_BYTES], PROT_SIZE_BYTE_ORDER), header[PROT_SIZE_BYTES]