import random
from abc import ABC, abstractmethod


class ErrorType(ABC):
    @abstractmethod
    def eval(self, value):
        return value


class Noise(ErrorType):
    def __init__(self, error_rate):
        self.err_rate = error_rate / 2

    def eval(self, value):
        adj = random.uniform(-self.err_rate, self.err_rate) * value
        return value + adj

    def __eq__(self, other):
        if isinstance(other, Noise):
            return other.err_rate == self.err_rate
        return False

    def __repr__(self):
        return f"noise({self.err_rate * 2:.2f})"

