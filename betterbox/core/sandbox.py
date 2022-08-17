from typing import Any, Callable
from .box import Box

class SafeBox:
    """
    Auxiliar class that uses a callback to return exposed functions
    """
    def __init__(self, wrap: Callable) -> None:
        self.__wrap = wrap

    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            try:
                return self.__wrap(name)
            except AttributeError:
                raise e

def create_safe_self(box, exposed_functions):
    """
    Returns a instance of a SafeBox with custom reference box and exposed_functions dict
    """
    def getattr(name: str) -> Any:
        try:
            fn = exposed_functions[name]
            return lambda *args, **kwargs: fn(box, *args, **kwargs)
        except KeyError as e:
            raise AttributeError(str(e))
    return SafeBox(getattr)

class SandBox(Box):
    """
    Allows injecting functions for execution in a controlled environment on a box
    """
    def inject(self, fn: Callable, use_self: bool = False):
        if use_self:
            __safe_self = create_safe_self(self, self.exposed_functions)
            setattr(self, fn.__name__, lambda _, *args, **kwargs: fn(__safe_self, *args, **kwargs))            
        else:
            setattr(self, fn.__name__, lambda _, *args, **kwargs: fn(*args, **kwargs))

class UnsafeSandBox(SandBox):
    """
    Unsafe version of the SandBox, does not wrap the self object so the injected function can take control of the box
    """
    def inject(self, fn: Callable, use_self: bool = False):
        if use_self:
            setattr(self, fn.__name__, lambda unsafe_self, *args, **kwargs: fn(unsafe_self, *args, **kwargs))            
        else:
            setattr(self, fn.__name__, lambda _, *args, **kwargs: fn(*args, **kwargs))