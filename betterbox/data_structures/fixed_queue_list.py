from queue import Queue
from typing import Any, Tuple, Union
from threading import Lock

from .promise import Promise
from .reusable_list import MemberId, ReusableList

class FixedQueueList:
    __slots__ = '__buffer',

    def __init__(self):
        self.__buffer: ReusableList = ReusableList()

    def reserve(self, size: int) -> Tuple[Promise, MemberId]:
        id = self.__buffer.append((size, Queue(size)))
        if element := self.__buffer.get(id):
            size, q = element
            return Promise(q, size), id
        else:
            raise RuntimeError('Created fixed queue does not exist')

    def put(self, id: MemberId, data: Any):
        if element := self.__buffer.get(id):
            size, q = element
            q.put(data)
            if q.qsize() >= size:
                self.__buffer.remove(id)