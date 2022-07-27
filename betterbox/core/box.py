from __future__ import annotations
from types import FunctionType

def private(func: FunctionType):
    setattr(func, 'private', True)
    return func

class MetaBox(type):
    def __new__(cls, name, bases, dict):
        data = super().__new__(cls, name, bases, dict)
        setattr(data, 'exposed_functions', {})
        for attr, obj in data.__dict__.items():
            if callable(obj) and (not hasattr(obj, 'private') or not getattr(obj, 'private')):
                data.exposed_functions[attr] = obj
        return data

class Box(metaclass=MetaBox):
    __instance: Box = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

def serve_box(port):
    def serve_box_box(target_box):
        return target_box
    return serve_box_box