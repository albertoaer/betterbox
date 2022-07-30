from .box import Box, private
from types import Any, List

from ..networking import Client

class BoxClient:
    def __init__(self) -> None:
        self.clients: List[Client] = []

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
            self.__client.clients.append(connections[c])
            c += 1
        for i in range(c, len(connections)):
            connections[i].close()

    def __getattribute__(self, name: str) -> Any:
        if hasattr(self, name): super().__getattribute__(name)
        

def use_box(port):
    def use_box_box(target_box: type[RemoteBox]):
        connections = [] #Use an algorithm to find the boxes
        target_box.instance().include_boxes(connections)
        return target_box
    return use_box_box