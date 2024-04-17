import abc
import json

import requests

from utils.timing import timed


class VectorEmitter:
    """
    The abstract base class of an emitter. Each emitter directs the data output to a different source.
    """
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
        with open(self.filename, "a+") as f:
            f.write(out_str)


class TsvVectorEmitter(VectorEmitter):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def emit_vector(self, vector):
        out_str = f"{vector[0]}\t{vector[1]}\t{vector[2]}\n"
        with open(self.filename, "a+") as f:
            f.write(out_str)


class EndpointVectorEmitter(VectorEmitter):
    def __init__(self, endpoint):
        super().__init__()
        self.endpoint = endpoint
        self.session = requests.Session()

    @timed
    def emit_vector(self, vector):
        payload = {
            "x": vector[0],
            "y": vector[1],
            "z": vector[2]
        }
        response = self.session.put(
            url=self.endpoint,
            data=json.dumps(payload),
            headers={
                "Content-Type": "application/json",
                "Connection": "keep-alive"
            }
        )
        print(f"Response {response.status_code} from {self.endpoint}\n{json.dumps(response.text, indent=4)}")
