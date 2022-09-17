from __future__ import annotations
from socket import gethostbyname
from tkinter import E
import traceback
from typing import Any, Type, Callable
from typing_extensions import Self

from betterbox.serialization.messages import MessageType, RegisterFunctionMessage

from ..networking import Server
from ..data_structures import MemberId
from ..serialization import Message, ExposedFunctionsMessage, ReturnValueMessage

def private(func: Callable):
    setattr(func, 'private', True)
    return func

def do_expose(obj: Callable):
    return callable(obj) and (not hasattr(obj, 'private') or not getattr(obj, 'private'))

class MetaBox(type):
    def __new__(cls, name, bases, dict):
        data = super().__new__(cls, name, bases, dict)
        exposed = {}
        if hasattr(data, 'exposed_functions'):
            exposed.update(data.exposed_functions)
        setattr(data, 'exposed_functions', exposed)
        for attr, obj in data.__dict__.items():
            if do_expose(obj):
                data.exposed_functions[attr] = obj
        return data

class BoxServerException(Exception): pass

class BoxServer:
    def __init__(self, box: Box, addr: str, port: int) -> None:
        self.box = box
        self.server = Server(addr, port)
        self.server.on_connect(self.__new_connection)
        self.server.start(lambda client, msg: self.__message_handle(client, Message.deserialize(msg)))

    def __new_connection(self, client: MemberId):
        self.server.emit(client, ExposedFunctionsMessage(
            list(self.box.exposed_functions.keys())).serialize())

    def __message_handle(self, client: MemberId, msg: Message):
        try:
            if msg.type == MessageType.Invokation:
                result = self.box.exposed_functions[msg.data["name"]](self.box, *msg.data["args"], **msg.data["kwargs"])
                self.server.emit(client, ReturnValueMessage(msg.data["retaddr"], result).serialize())
        except Exception as e:
            print(f"Exception catched: {e}, {traceback.format_exc()}")

    def broadcast(self, msg: Message):
        for client in self.server.clients:
            self.server.emit(client, msg.serialize())

class Box(metaclass=MetaBox):
    @private
    def serve_once(self, addr: str, port: int):
        if hasattr(self, 'server'):
            raise BoxServerException('A box can only be served once')
        self.server = BoxServer(self, addr, port)

    def __setattr__(self, name: str, value: Any):
        super().__setattr__(name, value)
        if do_expose(value):
            self.exposed_functions[name] = value
            self.server.broadcast(RegisterFunctionMessage(name))

    @classmethod
    def instance(cls) -> Self:
        if not '__instance' in cls.__dict__.keys():
            setattr(cls, '__instance', cls())
        return cls.__dict__['__instance']

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