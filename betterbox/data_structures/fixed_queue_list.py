from queue import Queue
from typing import Any, Union

from betterbox.data_structures.promise import Promise
from .reusable_list import MemberId, ReusableList

class FixedQueueList:
    def __init__(self):
        self.__buffer: ReusableList = ReusableList()

    def reserve(self, size: int) -> MemberId:
        id = self.__buffer.append((size, Queue(size)))
        return id

    def put(self, id: MemberId, data: Any) -> bool:
        if element := self.__buffer.get(id):
            size, q = element
            q.put(data)
            if q.qsize() >= size:
                self.__buffer.remove(id)
                return True
        return False
    
    def close(self, id: MemberId):
        self.__buffer.remove(id)

    def promise_for(self, id: MemberId) -> Union[Promise, None]:
        if element := self.__buffer.get(id):
            size, q = element
            return Promise(q, size, lambda:self.close(id))
        return None