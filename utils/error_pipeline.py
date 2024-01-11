import random
from abc import ABC, abstractmethod


class ErrorType(ABC):
    @abstractmethod
    def eval(self, value):
        raise NotImplementedError


class Noise(ErrorType):
    def __init__(self, error_rate):
        if error_rate > 1 or error_rate < 0:
            raise ValueError("Noise error rate must be between 0 and 1")
        self.err_rate = error_rate

    def eval(self, value):
        adj = random.uniform(-self.err_rate, self.err_rate) * value
        return value + adj

    def __eq__(self, other):
        if isinstance(other, Noise):
            return other.err_rate == self.err_rate
        return False

    def __repr__(self):
        return f"noise({self.err_rate:.2f})"

