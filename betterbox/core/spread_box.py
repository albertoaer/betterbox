from __future__ import annotations
from typing import Callable, Dict, List, Tuple, Union

from ..data_structures import Promise, PromiseArray
from .group_box import GroupBox

class SpreadBox(GroupBox):
    def spread(self, fn: Union[str, Callable], vector: List[Tuple[Tuple, Dict]], use_self: bool = False) -> Promise:
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