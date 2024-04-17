"""
Defines how data can be emitted from the program.
"""
import abc
import json

import requests

from utils.timing import timed


class VectorEmitter:
    """
    The abstract base class of an emitter. Each emitter directs the data output to a different source.
    """
    @abc.abstractmethod
    def emit_vector(self, vector: list[float]) -> None:
        """
        Method to override to enable the functionality of the emitter

        Args:
            vector: a list of floats in the form [x, y, z]

        Returns:
            None
        """
        raise NotImplementedError("You must override emit_vector()")


class StdOutVectorEmitter(VectorEmitter):
    """
    Emitter that prints the data to the console.
    """
    def emit_vector(self, vector: list[float]) -> None:
        """
        Prints the vector to the console
        Args:
            vector: a list of floats in the form [x, y, z]

        Returns:
            None
        """
        print(vector)


class CsvVectorEmitter(VectorEmitter):
    """
    Emitter that writes to a csv file.
    """
    def __init__(self, filename: str):
        """
        Prepares to write a csv file

        Args:
            filename: The path to the csv file to write to.
        """
        super().__init__()
        self.filename = filename

    def emit_vector(self, vector: list[float]) -> None:
        """
        Writes the vector to a csv file
        Args:
            vector: a list of floats in the form [x, y, z]

        Returns:
            None
        """
        out_str = f"{vector[0]},{vector[1]},{vector[2]}\n"
        with open(self.filename, "a+") as f:
            f.write(out_str)


class TsvVectorEmitter(VectorEmitter):
    """
    Emitter that writes to a tsv file.
    """
    def __init__(self, filename: str):
        """
        Prepares to write a tsv file

        Args:
            filename: The path to the tsv file to write to.
        """
        super().__init__()
        self.filename = filename

    def emit_vector(self, vector: list[float]) -> None:
        """
        Writes the vector to a tsv file
        Args:
            vector: a list of floats in the form [x, y, z]

        Returns:
            None
        """
        out_str = f"{vector[0]}\t{vector[1]}\t{vector[2]}\n"
        with open(self.filename, "a+") as f:
            f.write(out_str)


class EndpointVectorEmitter(VectorEmitter):
    """
    Emitter that writes to an endpoint.
    """
    def __init__(self, endpoint: str):
        """
        Opens a session with the provided endpoint in preparation for sending data.

        Args:
            endpoint: the url of the endpoint to create the session with.
        """
        super().__init__()
        self.endpoint = endpoint
        self.session = requests.Session()

    @timed
    def emit_vector(self, vector: list[float]) -> None:
        """
        Makes a PUT request to the configured endpoint with x, y, and z, coordinates as the body of the PUT request.
        Args:
            vector: a list of floats in the form [x, y, z]

        Returns:
            None
        """
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
