from .reusable_list import ReusableList
import pytest

def test_append_len():
    l = ReusableList()
    first = l.append(1)
    assert len(l.collection) == 1
    assert len(l) == 1
    l.append(2)
    assert len(l.collection) == 2
    assert len(l) == 2
    l.remove(first)
    assert len(l.collection) == 2 #Phisycal size still the same
    assert len(l) == 1
    l.append(3)
    assert len(l.collection) == 2
    assert len(l) == 2

def test_correct_hash():
    l = ReusableList()
    x = l.append(5)
    assert x[0] == 0
    assert x[1] == hash(5)
    assert l.get(x) == 5
    l.remove(x)
    assert l.get(x) == None

def test_iterate():
    l = ReusableList()
    l.append(1)
    x = l.append(2)
    l.append(3)
    l.remove(x)
    elements = iter(l)
    assert l[next(elements)] == 1
    assert l[next(elements)] == 3
    with pytest.raises(StopIteration):
        next(elements)