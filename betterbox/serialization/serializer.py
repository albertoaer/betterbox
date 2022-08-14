import dill

class Serializer:
    def dumps(self, obj: any) -> bytes:
        return dill.dumps(obj)

    def loads(self, data: bytes) -> any:
        return dill.loads(data)

serializer = Serializer()