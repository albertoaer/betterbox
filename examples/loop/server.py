from betterbox import lock_box, serve_box, Box

@serve_box(8082)
@lock_box()
class Server(Box):
    def __init__(self) -> None:
        super().__init__()

    def update_message(self, message):
        print(message)