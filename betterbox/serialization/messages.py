from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List
from .serializer import serializer

class NotAMessageException(Exception): pass

class MessageType(Enum):
    ExposedFunctions = 0, #Notify exposed functions
    Invokation = 1, #Invoke a exposed function
    ReturnValue = 2, #Send the return of an invokation back

class Message:
    __slots__ = 'type', 'data'

    def __init__(self, type: MessageType, data: Any) -> None:
        self.type = type
        self.data = data

    def serialize(self) -> str:
        return serializer.dumps(self)

    @staticmethod
    def deserialize(str) -> Message:
        msg = serializer.loads(str)
        if not isinstance(msg, Message):
            raise NotAMessageException('The strings does not represents a message')
        return msg

class ExposedFunctionsMessage(Message):
    def __init__(self, fns: List[str]) -> None:
        super().__init__(MessageType.ExposedFunctions, fns)

class InvokationMessage(Message):
    def __init__(self, retaddr: Any, name: str, args: List, kwargs: Dict) -> None:
        super().__init__(MessageType.Invokation, {"retaddr": retaddr, "name": name, "args": args, "kwargs": kwargs})

class ReturnValueMessage(Message):
    def __init__(self, retaddr: Any, value: Any) -> None:
        super().__init__(MessageType.ReturnValue, {"retaddr": retaddr, "value": value})