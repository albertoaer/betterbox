from .protocol import *

def test_headers_serialization():
    action, len = PROT_ACTION_NOTIFY, 400
    assert deserialize_header(serialize_header(len, action)) == (len, action)
    action, len = PROT_ACTION_PING, 122
    assert deserialize_header(serialize_header(len, action)) == (len, action)
    action, len = PROT_ACTION_APP, 22006
    assert deserialize_header(serialize_header(len, action)) == (len, action)

def test_headers_config_update():
    assert serialize_header(4, 0)[0] == 4 #If byte order is little (the default), at the beginning must be the greatest value
    set_protocol_config(5, 'big')
    assert max_value() == (2 ** (8 * 5)) - 1 #Check if the formula is correct
    assert len(serialize_header(4, 0)) == 6 #Check if the length is size bytes + action byte
    assert serialize_header(4, 0)[0] == 0 #If byte order is big, at the beginning must be the lowest value