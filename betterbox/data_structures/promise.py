from abc import ABC, abstractmethod
from functools import reduce
from queue import Queue
from typing import Any, List, Callable

class ResourceExpirationException(Exception): pass

class PromiseBase(ABC):
    @abstractmethod
    def any(self) -> Any:
        pass

    def all(self) -> List[Any]:
        res = []
        try:
            while True:
                res.append(self.any())
        except ResourceExpirationException:
            pass
        return res

    def compute(self, fn: Callable) -> Any:
        res = self.all()
        return reduce(fn, res)

class Promise(PromiseBase):
    def __init__(self, queue: Queue, total: int, close: Callable):
        super().__init__()
        self.__queue = queue
        self.__total = total
        self.__close = close

    def any(self) -> Any:
        if self.__total <= 0:
            raise ResourceExpirationException('All the Promise expected responses have been read')
        self.__total -= 1
        return self.__queue.get(block=True)

    def __del__(self):
        self.__close()

class PromiseArray(PromiseBase):
    def __init__(self, promises: List[PromiseBase]) -> None:
        super().__init__()
        self.__promises = promises
        self.__idx = 0

    def any(self) -> Any:
        if self.__idx >= len(self.__promises):
            raise ResourceExpirationException('No more promises left')
        try:
            return self.__promises[self.__idx].any()
        except ResourceExpirationException:
            self.__idx += 1
            return self.any()