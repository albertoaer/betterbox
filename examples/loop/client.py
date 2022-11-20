from betterbox import use_local_box, RemoteBox
from sys import argv

@use_local_box(8082)
class Client(RemoteBox):
    def __init__(self) -> None:
        super().__init__()

    def send(self, msg):
        self.update_message(msg)

if __name__ == '__main__' and len(argv) > 1:
    Client.instance().require(1).send(argv[1])