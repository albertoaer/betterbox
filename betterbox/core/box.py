from __future__ import annotations
from socket import gethostbyname
from types import FunctionType
from typing import Type

from betterbox.serialization.messages import MessageType

from ..networking import Server
from ..data_structures.reusable_list import MemberId
from ..serialization import Message, ExposedFunctionsMessage

def private(func: FunctionType):
    setattr(func, 'private', True)
    return func

class MetaBox(type):
    def __new__(cls, name, bases, dict):
        data = super().__new__(cls, name, bases, dict)
        setattr(data, 'exposed_functions', {})
        for attr, obj in data.__dict__.items():
            if callable(obj) and (not hasattr(obj, 'private') or not getattr(obj, 'private')):
                data.exposed_functions[attr] = obj
        return data

class BoxServerException(Exception): pass

class BoxServer:
    def __init__(self, box: Box, port: int) -> None:
        self.box = box
        #TODO: Avoid address and family hardcoding
        self.server = Server(gethostbyname('localhost'), port)
        self.server.on_connect(self.new_connection)
        self.server.start(lambda client, msg: self.message_handle(client, Message.deserialize(msg)))

    def new_connection(self, client: MemberId):
        self.server.emit(client, ExposedFunctionsMessage(
            list(self.box.exposed_functions.keys())).serialize())

    def message_handle(self, client: MemberId, msg: Message):
        if msg.type == MessageType.Invokation:
            self.box.exposed_functions[msg.data["name"]](self.box, *msg.data["args"], **msg.data["kwargs"])

class Box(metaclass=MetaBox):
    __instance: Box = None

    def __init__(self) -> None:
        self.__server: BoxServer = None

    @private
    def serve_once(self, port: int):
        if self.__server:
            raise BoxServerException('A box can only be served once')
        self.__server = BoxServer(self, port)

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

def serve_box(port: int):
    def serve_box_box(target_box: Type[Box]):
        target_box.instance().serve_once(port)
        return target_box
    return serve_box_box