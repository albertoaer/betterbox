from typing import Iterator

from ..networking import Client
from .remote_box import RemoteBox
from .box import private

class GroupBox(RemoteBox):
    @private
    def include_boxes(self, connections: Iterator[Client]):
        """
        Include all the connections from a iterator as boxes
        """
        self.prepare_client()
        for conn in connections:
            self.client.include_client(conn)