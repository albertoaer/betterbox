from socket import gethostbyname
from threading import Semaphore
from typing import Any, Iterator, List, Dict, Type

from .box import Box, private

from ..networking import Client, get_available_boxes
from ..data_structures.reusable_list import ReusableList, MemberId
from ..data_structures.fixed_queue_list import FixedQueueList
from ..serialization import Message, MessageType, InvokationMessage

class BoxClient:
    def __init__(self) -> None:
        self.clients: ReusableList = ReusableList()
        self.exposed_functions: Dict[str, MemberId] = {}
        self.returns: FixedQueueList = FixedQueueList()
        self.wait_exposed_functions: Semaphore = Semaphore(0)

    def include_client(self, client: Client):
        id = self.clients.append(client)
        client.start(lambda msg: self.handle_message(id, Message.deserialize(msg)))
        self.wait_exposed_functions.acquire()

    def handle_message(self, id: MemberId, msg: Message):
        if msg.type == MessageType.ExposedFunctions:
            for fn in msg.data:
                self.exposed_functions.setdefault(fn, [])
                self.exposed_functions[fn].append(id)
            self.wait_exposed_functions.release()
        elif msg.type == MessageType.ReturnValue:
            self.returns.put(msg.data['retaddr'], msg.data['value'])
    
    def try_get(self, name):
        if owners := self.exposed_functions.get(name):
            def invoke(*args, **kwargs):
                retaddr = self.returns.reserve(len(owners))
                for id in owners:
                    if client := self.clients[id]:
                        client.emit(InvokationMessage(retaddr, name, args, kwargs).serialize())
                return self.returns.promise_for(retaddr)
            return invoke
        return None

class RemoteBox(Box):
    def __init__(self) -> None:
        super().__init__()
        self.__client: BoxClient = None

    @private
    def include_boxes(self, connections: Iterator[Client]):
        """
        From a list of found connections selects one (the first)
        The rest of the found connections are discarted

        Maybe would be better a client iterator as input 
        """
        if not self.__client:
            self.__client = BoxClient()
        for conn in connections:
            self.__client.include_client(conn)
            break

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return self.__client.try_get(name)
        

def aux_include(target_box: Type[RemoteBox], connections: Iterator[Client]) -> Type[RemoteBox]:
    target_box.instance().include_boxes(connections)
    return target_box

def use_box(port: int, interface: str):
    def use_box_box(target_box: Type[RemoteBox]):
        return aux_include(target_box, get_available_boxes(interface, port))
    return use_box_box

def use_know_box(port: int, *addrs: List[str]):
    def use_know_box_box(target_box: Type[RemoteBox]):
        connections = map(lambda addr: Client(addr, port), addrs)
        return aux_include(target_box, connections)
    return use_know_box_box

def use_local_box(port: int):
    def use_local_box_box(target_box: Type[RemoteBox]):
        return aux_include(target_box, [Client(gethostbyname('localhost'), port)])
    return use_local_box_box