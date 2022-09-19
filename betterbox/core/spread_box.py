from __future__ import annotations
from typing import Callable, Dict, List, Tuple, Union

from ..data_structures import Promise, PromiseArray
from .group_box import GroupBox

class SpreadBox(GroupBox):
    """
    GroupBox specialization that supports dividing tasks between its boxes
    """
    def spread(self, fn: Union[str, Callable], vector: List[Tuple[Tuple, Dict]], use_self: bool = False) -> Promise:
        """
        Each member of the 'vector' must be applied to the 'fn' operation

        - fn : Union[str, Callable]
            is ensured to exists in every client box otherwise is created

        - vector : List[Tuple[Tuple, Dict]]
            is divided between the client boxes

        If the 'fn' function is a callable all the boxes must support injection

        Returns a Promise    
        """
        name = fn
        if callable(fn):
            name = fn.__name__
            self.inject(fn, use_self).all() #Inject the function and await all
        targets = self.client.try_get_divided(name)
        if len(targets) == 0:
            raise RuntimeError('Not enough clients to perform the task')

        promises = []
        for i, v in enumerate(vector):
            promise = targets[i%len(targets)](*v[0], **v[1])
            promises.append(promise)

        return PromiseArray(promises)

class SpreadAdapter:
    """
    Auxiliar class to wrap a SpreadBox and simplify the vector generation process
    """
    def __init__(self, target: SpreadBox, cumulative: bool = False) -> None:
        self.__target = target
        self.__arg_list: List[Tuple[Tuple, Dict]] = []
        self.__cumulative = cumulative

    def spread(self, fn: Union[str, Callable], use_self: bool = False) -> Promise:
        returns = self.__target.spread(fn, self.__arg_list, use_self)
        if not self.__cumulative:
            self.clear()
        return returns

    def submit(self, *args, **kwargs):
        self.__arg_list.append((args, kwargs))

    def clear(self):
        self.__arg_list = []

    def __enter__(self) -> SpreadAdapter:
        return self
  
    def __exit__(self, *_):
        pass