import random
from abc import ABC, abstractmethod
from typing import Callable


class ErrorType(ABC):
    @abstractmethod
    def eval(self, vector: tuple[float, float, float], *args, **kwargs):
        """
        Applies some error processing to an [x y z] vector
        Args:
            vector: [x y z] vector of a depth reading

        Returns:
            new_vector: an [x y z] vector with some error applied to it.
        """
        raise NotImplementedError


class Noise(ErrorType):
    def __init__(self, error_rate):
        """
        Adds random noise according to the error rate to the z component of a vector

        Args:
            error_rate: the error range to apply. Must be between 0 and 1.
        """
        if error_rate > 1 or error_rate < 0:
            raise ValueError("Noise error rate must be between 0 and 1")
        self.err_rate = error_rate

    def eval(self, vector, seed=None, *args, **kwargs):
        """
        Applies random vertical (z) noise error processing to an [x y z] vector
        Args:
            vector: [x y z] vector of a depth reading
            seed: [Optional] a seed to give to the random number generator

        Returns:
            new_vector: an [x y z] vector with some error applied to it.
        """
        random.seed(seed)
        new_vector = (vector[0], vector[1], vector[2] + random.uniform(-self.err_rate, self.err_rate) * vector[2])
        return new_vector

    def __eq__(self, other):
        if isinstance(other, Noise):
            return other.err_rate == self.err_rate
        return False

    def __repr__(self):
        return f"noise({self.err_rate:.2f})"


def run_pipeline(errs: list[ErrorType], vector: tuple[float, float, float], *args, **kwargs) \
        -> tuple[float, float, float]:
    """
    Takes a list of error types and runs the provided vector, args, and kwargs, through a pipeline
    sequentially according to the order of errs

    Args:
        errs: a list of ErrorType objects
        vector: an [x y z] vector to be processed

    Returns:
        new_vector: The processed [x y z] vector after being run through the pipeline
    """
    new_vector = vector
    for e in errs:
        new_vector = e.eval(new_vector, *args, **kwargs)
    return new_vector
