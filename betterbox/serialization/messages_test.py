from .messages import MessageType, Message, ExposedFunctionsMessage, InvokationMessage, ReturnValueMessage

def test_exposed_functions_message():
    fns = ["A", "B", "C"]
    e = ExposedFunctionsMessage(fns)
    s = e.serialize()
    m = Message.deserialize(s)
    assert m.type == MessageType.ExposedFunctions
    assert m.data == e.data
    assert m.data == fns

def test_invokation_message():
    l = 44
    args = ["abc", 3]
    kwargs = {"test":8}
    e = InvokationMessage(l, args, kwargs)
    s = e.serialize()
    m = Message.deserialize(s)
    assert m.type == MessageType.Invokation
    assert m.data == e.data
    assert m.data["retaddr"] == l
    assert m.data["args"] == args
    assert m.data["kwargs"] == kwargs

def test_return_value_message():
    l = 5
    value = "A return value!"
    e = ReturnValueMessage(l, value)
    s = e.serialize()
    m = Message.deserialize(s)
    assert m.type == MessageType.ReturnValue
    assert m.data == e.data
    assert m.data["retaddr"] == l
    assert m.data["value"] == value