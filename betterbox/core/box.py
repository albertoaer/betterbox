from __future__ import annotations
from socket import gethostbyname
from typing import Type, Callable
from typing_extensions import Self

from betterbox.serialization.messages import MessageType

from ..networking import Server
from ..data_structures.reusable_list import MemberId
from ..serialization import Message, ExposedFunctionsMessage, ReturnValueMessage

def private(func: Callable):
    setattr(func, 'private', True)
    return func

class MetaBox(type):
    def __new__(cls, name, bases, dict):
        data = super().__new__(cls, name, bases, dict)
        if not hasattr(data, 'exposed_functions'):
            setattr(data, 'exposed_functions', {})
        for attr, obj in data.__dict__.items():
            if callable(obj) and (not hasattr(obj, 'private') or not getattr(obj, 'private')):
                data.exposed_functions[attr] = obj
        return data

class BoxServerException(Exception): pass

class BoxServer:
    def __init__(self, box: Box, addr: str, port: int) -> None:
        self.box = box
        self.server = Server(addr, port)
        self.server.on_connect(self.new_connection)
        self.server.start(lambda client, msg: self.message_handle(client, Message.deserialize(msg)))

    def new_connection(self, client: MemberId):
        self.server.emit(client, ExposedFunctionsMessage(
            list(self.box.exposed_functions.keys())).serialize())

    def message_handle(self, client: MemberId, msg: Message):
        if msg.type == MessageType.Invokation:
            result = self.box.exposed_functions[msg.data["name"]](self.box, *msg.data["args"], **msg.data["kwargs"])
            self.server.emit(client, ReturnValueMessage(msg.data["retaddr"], result).serialize())

class Box(metaclass=MetaBox):
    __instance: Box = None

    @private
    def serve_once(self, addr: str, port: int):
        if hasattr(self, '__server'):
            raise BoxServerException('A box can only be served once')
        self.__server = BoxServer(self, addr, port)

    @classmethod
    def instance(cls) -> Self:
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

def serve_box(port: int, expose: bool = False):
    def serve_box_box(target_box: Type[Box]):
        addr = '0.0.0.0' if expose else gethostbyname('localhost')
        target_box.instance().serve_once(addr, port)
        return target_box
    return serve_box_box

def serve_box_at(port: int, addr: str):
    def serve_box_at_box(target_box: Type[Box]):
        target_box.instance().serve_once(addr, port)
        return target_box
    return serve_box_at_box