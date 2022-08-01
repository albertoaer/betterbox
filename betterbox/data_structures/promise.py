from functools import reduce
from queue import Queue
from types import FunctionType
from typing import Any, List

class ResourceExpirationException(Exception): pass

class Promise:
    def __init__(self, queue: Queue, total: int, close: FunctionType):
        self.__queue = queue
        self.__total = total
        self.__close = close

    def any(self) -> Any:
        if self.__total <= 0:
            raise ResourceExpirationException('All the Promise expected responses have been read')
        self.__total -= 1
        return self.__queue.get(block=True)

    def all(self) -> List[Any]:
        res = []
        while self.__total > 0:
            res.append(self.any())
        return res

    def compute(self, fn: FunctionType) -> Any:
        res = self.all()
        return reduce(fn, res)

    def __del__(self):
        self.__close()