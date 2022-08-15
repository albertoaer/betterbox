from .box import Box

class A(Box):
    def a() -> str:
        return "a"

class B(A):
    def a() -> str:
        return "b"

class C(A):
    def c() -> str:
        return "c"

class D(Box):
    def d() -> str:
        return "d"

a = A.instance()
b = B.instance()
c = C.instance()
d = D.instance()

def test_exposed_dicts():
    assert a.exposed_functions.keys() == b.exposed_functions.keys()
    assert a.exposed_functions.keys() != c.exposed_functions.keys()
    assert a.exposed_functions.keys() != d.exposed_functions.keys()
    assert c.exposed_functions.keys() != d.exposed_functions.keys()

def test_exposed_return():
    assert a.exposed_functions['a']() == c.exposed_functions['a']()
    assert a.exposed_functions['a']() != b.exposed_functions['a']()