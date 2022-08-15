from typing import Any, Iterator, List, Tuple, Union

MemberId = Tuple[int, int]

class ReusableList:
    __slots__ = 'collection',

    def __init__(self) -> None:
        self.collection: List[Any] = []
        
    def __len__(self) -> int:
        length = 0
        for x in self.collection:
            if x:
                length += 1
        return length

    def append(self, item: Any) -> MemberId:
        pos, append = self.__find_empty()
        if append: self.collection.append(None)
        self.collection[pos] = item
        return self.id(pos)

    def __delitem__(self, id: MemberId):
        self.remove(id)

    def remove(self, id: MemberId):
        self.collection[id[0]] = None

    def __getitem__(self, id: MemberId) -> Union[Any, None]:
        return self.get(id)

    def get(self, id: MemberId) -> Union[Any, None]:
        got = self.collection[id[0]]
        if got:
            if hash(got) == id[1]:
                return got
        return None

    def id(self, pos: int) -> Union[MemberId, None]:
        got = self.collection[pos]
        if got: return pos, hash(got)
        return None

    def __find_empty(self) -> Tuple[int, bool]:
        for p, i in enumerate(self.collection):
            if i == None: return p, False
        return len(self.collection), True

    def __iter__(self) -> Iterator[MemberId]:
        for i in range(0, len(self.collection)):
            if id := self.id(i):
                yield id