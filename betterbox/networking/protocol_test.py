from .protocol import *

def test_status():
    action, len = PROT_ACTION_NOTIFY, 400
    assert split_status(get_status(action, len))[0] == action
    assert split_status(get_status(action, len))[1] >= len
    action, len = PROT_ACTION_PING, 122
    assert split_status(get_status(action, len))[0] == action
    assert split_status(get_status(action, len))[1] >= len
    action, len = PROT_ACTION_APP, 22006
    assert split_status(get_status(action, len))[0] == action
    assert split_status(get_status(action, len))[1] >= len