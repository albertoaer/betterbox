from typing import Any, Iterator, List, Tuple, Union

MemberId = Tuple[int, int]

class ReusableList:
    __slots__ = 'collection',

    def __init__(self) -> None:
        self.collection: List[Any] = []
        
    def __len__(self) -> int:
        return sum([int(bool(x)) for x in self.collection])

    def append(self, item: Any) -> MemberId:
        pos, append = self.__find_empty()
        if append: self.collection.append(None)
        self.collection[pos] = (hash(item), item) #The data is a hash of the item and the item
        return self.__id(pos)

    def __delitem__(self, id: MemberId):
        self.remove(id)

    def remove(self, id: MemberId):
        got = self.collection[id[0]]
        if got and got[0] == id[1]:
            self.collection[id[0]] = None

    def __getitem__(self, id: MemberId) -> Union[Any, None]:
        return self.get(id)

    def get(self, id: MemberId) -> Union[Any, None]:
        got = self.collection[id[0]]
        if got and got[0] == id[1]:
            return got[1]
        return None

    def __find_empty(self) -> Tuple[int, bool]:
        for p, i in enumerate(self.collection):
            if not i: return p, False
        return len(self.collection), True

    def __iter__(self) -> Iterator[MemberId]:
        for i in range(0, len(self.collection)):
            if id := self.__id(i):
                yield id

    def __id(self, pos: int) -> Union[MemberId, None]:
        if got := self.collection[pos]: return pos, got[0]
        return None