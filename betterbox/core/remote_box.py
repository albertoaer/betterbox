from socket import gethostbyname
from threading import Semaphore
from typing import Any, Callable, Iterator, List, Dict, Type, TypeVar

from .box import Box, private

from ..networking import Client, get_available_boxes
from ..data_structures import FixedQueueList, ReusableList, MemberId
from ..serialization import Message, MessageType, InvokationMessage

class BoxClient:
    def __init__(self) -> None:
        self.clients: ReusableList = ReusableList()
        self.exposed_functions: Dict[str, MemberId] = {}
        self.returns: FixedQueueList = FixedQueueList()
        self.wait_exposed_functions: Semaphore = Semaphore(0)

    def include_client(self, client: Client):
        id = self.clients.append(client)
        client.start(lambda msg: self.__handle_message(id, Message.deserialize(msg)))
        self.wait_exposed_functions.acquire()

    def __handle_message(self, id: MemberId, msg: Message):
        if msg.type == MessageType.ExposedFunctions:
            for fn in msg.data:
                self.exposed_functions.setdefault(fn, [])
                self.exposed_functions[fn].append(id)
            self.wait_exposed_functions.release()
        elif msg.type == MessageType.RegisterFunction:
            self.exposed_functions.setdefault(msg.data, [])
            self.exposed_functions[msg.data].append(id)
        elif msg.type == MessageType.ReturnValue:
            self.returns.put(msg.data['retaddr'], msg.data['value'])
    
    def try_get(self, name: str) -> Callable:
        if owners := self.exposed_functions.get(name):
            def invoke(*args, **kwargs):
                promise, retaddr = self.returns.reserve(len(owners))
                for id in owners:
                    if client := self.clients[id]:
                        client.emit(InvokationMessage(retaddr, name, args, kwargs).serialize())
                return promise
            return invoke
        raise AttributeError(f'No shared method {name}')

    def try_get_divided(self, name: str) -> List[Callable]:
        def make_invoke(client) -> Callable:
            def invoke(*args, **kwargs):
                promise, retaddr = self.returns.reserve(1)
                client.emit(InvokationMessage(retaddr, name, args, kwargs).serialize())
                return promise
            return invoke
        if owners := self.exposed_functions.get(name):
            return [make_invoke(client) for id in owners if (client := self.clients[id])]
        raise AttributeError(f'No shared method {name}')

RBoxT = TypeVar('RBoxT', bound='RemoteBox')

class RemoteBox(Box):
    @private
    def prepare_client(self):
        if not hasattr(self, 'client'):
            self.client = BoxClient()

    @private
    def include_boxes(self, connections: Iterator[Client]):
        """
        From a iterator of found connections selects one (the first)
        The rest of the found connections are discarted
        """
        self.prepare_client()
        self.client.include_client(next(connections))

    @private
    def require(self, expected: int) -> RBoxT:
        assert expected <= len(self.client.clients)
        return self

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as err:
            if name == 'client': raise err #Special case, avoid recursion searching client
            return self.client.try_get(name)
        

def aux_include(target_box: Type[RBoxT], connections: Iterator[Client]) -> Type[RBoxT]:
    target_box.instance().include_boxes(connections)
    return target_box

def use_box(port: int, interface: str):
    def use_box_box(target_box: Type[RBoxT]) -> Type[RBoxT]:
        return aux_include(target_box, iter(get_available_boxes(interface, port)))
    return use_box_box

def use_know_box(port: int, *addrs: List[str]):
    def use_know_box_box(target_box: Type[RBoxT]) -> Type[RBoxT]:
        connections = map(lambda addr: Client(addr, port), addrs)
        return aux_include(target_box, iter(connections))
    return use_know_box_box

def use_local_box(port: int):
    def use_local_box_box(target_box: Type[RBoxT]) -> Type[RBoxT]:
        return aux_include(target_box, iter([Client(gethostbyname('localhost'), port)]))
    return use_local_box_box