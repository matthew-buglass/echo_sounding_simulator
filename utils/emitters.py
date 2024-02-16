import abc
import requests


class VectorEmitter:
    @abc.abstractmethod
    def emit_vector(self, vector):
        raise NotImplementedError("You must override emit_vector()")


class StdOutVectorEmitter(VectorEmitter):
    def emit_vector(self, vector):
        print(vector)


class CsvVectorEmitter(VectorEmitter):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def emit_vector(self, vector):
        out_str = f"{vector[0]},{vector[1]},{vector[2]}\n"
        with open(self.filename) as f:
            f.write(out_str)


class TsvVectorEmitter(VectorEmitter):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def emit_vector(self, vector):
        out_str = f"{vector[0]}\t{vector[1]}\t{vector[2]}\n"
        with open(self.filename) as f:
            f.write(out_str)


class EndpointVectorEmitter(VectorEmitter):
    def __init__(self, endpoint):
        super().__init__()
        self.endpoint = endpoint

    def emit_vector(self, vector):
        body = {
            "x": vector[0],
            "y": vector[1],
            "z": vector[2]
        }
        requests.put(self.endpoint, data=body)
        print(vector)

