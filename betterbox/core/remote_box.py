from socket import gethostbyname

from .box import Box, private
from typing import Any, List, Dict, Type

from ..networking import Client
from ..data_structures.reusable_list import ReusableList, MemberId
from ..serialization import Message, MessageType, InvokationMessage

class BoxClient:
    def __init__(self) -> None:
        self.clients: ReusableList = ReusableList()
        self.exposed_functions: Dict[str, MemberId] = {}

    def include_client(self, client: Client):
        id = self.clients.append(client)
        client.start(lambda msg: self.handle_message(id, Message.deserialize(msg)))

    def handle_message(self, id: MemberId, msg: Message):
        if msg.type == MessageType.ExposedFunctions:
            for fn in msg.data:
                self.exposed_functions.setdefault(fn, [])
                self.exposed_functions[fn].append(id)
    
    def try_get(self, name):
        if owners := self.exposed_functions.get(name):
            def invoke(*args, **kwargs):
                for id in owners:
                    if client := self.clients[id]: 
                        #Solve temporal channel 0
                        client.emit(InvokationMessage(0, name, args, kwargs).serialize())
            return invoke
        return None

class RemoteBox(Box):
    def __init__(self) -> None:
        super().__init__()
        self.__client: BoxClient = None

    @private
    def include_boxes(self, connections: List[Client]):
        """
        From a list of found connections selects one (the first)
        The rest of the found connections are discarted

        Maybe would be better a client iterator as input 
        """
        if not self.__client:
            self.__client = BoxClient()
        c = 0
        if len(self.__client.clients) == 0:
            self.__client.include_client(connections[c])
            c += 1
        for i in range(c, len(connections)):
            connections[i].close()

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return self.__client.try_get(name)
        

def use_box(port: int):
    def use_box_box(target_box: Type[RemoteBox]):
        connections = [] #TODO: Use an algorithm to find the boxes
        target_box.instance().include_boxes(connections)
        return target_box
    return use_box_box

def use_local_box(port: int):
    def use_local_box_box(target_box: Type[RemoteBox]):
        #TODO: Await the boxes to be connected in order to return
        target_box.instance().include_boxes([Client(gethostbyname('localhost'), port)])
        return target_box
    return use_local_box_box