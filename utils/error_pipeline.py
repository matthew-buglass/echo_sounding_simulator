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


def create_pipeline(errs: list[ErrorType]) -> Callable[[tuple[float, float, float]], tuple[float, float, float]]:
    """
    Takes a list of error types and build a composite function for the error pipeline

    Args:
        errs: a list of ErrorType objects

    Returns:
        pipeline_func: a function that takes a raw [x y z] vector and returns a processed [x y z] vector
    """
    def pipeline_func(vec): return errs[0].eval(vec)
    for e in errs[1:]:
        pipeline_func = e.eval(pipeline_func)
    return pipeline_func
