"""
Declares and maintains handlers for error types to be used in the pipeline
"""
import random
from abc import ABC, abstractmethod

import numpy as np

from utils.geometry import get_x_y_rotated_vector, point_in_tri


class ErrorType(ABC):
    @abstractmethod
    def eval(self, vector: tuple[float, float, float], *args, **kwargs) -> tuple[float, float, float]:
        """
        Applies some error processing to an [x y z] vector
        Args:
            vector: [x y z] vector of a depth reading

        Returns:
            new_vector: an [x y z] vector with some error applied to it.
        """
        raise NotImplementedError


class Noise(ErrorType):
    def __init__(self, error_rate: float, *args, **kwargs):
        """
        Adds random noise according to the error rate to the z component of a vector

        Args:
            error_rate: the error range to apply. Must be between 0 and 1.
        """
        super(Noise, self).__init__(*args, **kwargs)

        if error_rate > 1 or error_rate < 0:
            raise ValueError("Noise error rate must be between 0 and 1")
        self.err_rate = error_rate
        self.mean = 0
        # We want our error rate to be the 3-sigma bounds, or about 99.9973% of readings within it
        self.stddev = error_rate / 3

    def eval(self, vector: tuple[float, float, float], seed: float = None, *args, **kwargs) \
            -> tuple[float, float, float]:
        """
        Applies random vertical (z) noise error processing to an [x y z] vector
        Args:
            vector: [x y z] vector of a depth reading
            seed: [Optional] a seed to give to the random number generator

        Returns:
            new_vector: an [x y z] vector with some error applied to it.
        """
        random.seed(seed)
        new_vector = (vector[0], vector[1], vector[2] + random.gauss(self.mean, self.stddev) * vector[2])
        return new_vector

    def __eq__(self, other):
        if isinstance(other, Noise):
            return other.err_rate == self.err_rate
        return False

    def __repr__(self):
        return f"noise({self.err_rate:.2f})"


class FalseBottom(ErrorType):
    def __init__(self, debris_size=10, seed=None, *args, **kwargs):
        """
        Will generate a rectangular debris object of a given size in square meters at a random location
        Args:
            debris_size: The size of the debris object in
            seed: A random seed for testing
        """
        super(FalseBottom, self).__init__(*args, **kwargs)

        self.seed = seed
        random.seed(self.seed)

        self.length = random.random() * (debris_size - 1)
        self.width = debris_size / self.length

        self.debris_tris = []
        self.depth = 0

    def init_debris(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        """
        Initializes the debris
        Args:
            min_x: The min horizontal value of the mesh
            min_y: The min vertical value of the mesh
            max_x: The max horizontal value of the mesh
            max_y:  The max vertical value of the mesh

        Returns:
            None
        """
        random.seed(self.seed)

        # get a random point in the mesh
        p1 = np.asarray([random.random() * (max_x - min_x) + min_x, random.random() * (max_y - min_y) + min_y])

        #  P2 --- P4
        #  |      |
        #  |      |
        #  P1 --- P3
        # Get the point rotations about p1
        theta = random.random() * 2 * np.pi

        p2_pre = np.asarray([self.length, 0])
        p3_pre = np.asarray([0, self.width])
        p4_pre = np.asarray([self.length, self.width])

        p2 = p1 + get_x_y_rotated_vector(p2_pre, theta)
        p3 = p1 + get_x_y_rotated_vector(p3_pre, theta)
        p4 = p1 + get_x_y_rotated_vector(p4_pre, theta)

        # Triangles that form the rectangle:
        #  P2 --- P4
        #  |      |
        #  |      |
        #  P1 --- P3
        self.debris_tris = [(p1, p2, p4), (p1, p3, p4)]

    def eval(self, vector: tuple[float, float, float], *args, **kwargs) -> tuple[float, float, float]:
        """
        Applies random vertical (z) noise error processing to an [x y z] vector
        Args:
            vector: [x y z] vector of a depth reading

        Returns:
            new_vector: an [x y z] vector with some error applied to it.
        """
        if any([point_in_tri((vector[0], vector[1]), p1, p2, p3) for p1, p2, p3 in self.debris_tris]):
            if self.depth == 0:
                self.depth = vector[2] / 2
            return vector[0], vector[1], self.depth
        else:
            return vector


class Dropout(ErrorType):
    def __init__(self, error_rate: float, drop_off_rate=0.02, *args, **kwargs):
        """
        Adds a random chance of a sensor failing, with a stochastic falloff

        Args:
            error_rate: the error rate to apply. Must be between 0 and 1.
        """
        super(Dropout, self).__init__(*args, **kwargs)

        if error_rate > 1 or error_rate < 0:
            raise ValueError("Noise error rate must be between 0 and 1")
        self.err_rate = error_rate

        # Stochastic falloff hyperparameters
        self.drops_in_a_row = 0
        self.drop_off = drop_off_rate

    def _dropout_chance_(self) -> float:
        """
        Calculates the change of hte sensor dropping out
        Returns:
            drop_chance: A percent change that the sensor will drop out
        """
        stochastic_modification = self.drop_off / self.drops_in_a_row if self.drops_in_a_row > 0 else 0
        drop_off_chance = self.err_rate + stochastic_modification

        return drop_off_chance

    def eval(self, vector: tuple[float, float, float], seed=None, *args, **kwargs) -> tuple[float, float, float]:
        """
        Randomly, according to its error rate instantiation, causes a sensor dropout
        Args:
            vector: [x y z] vector of a depth reading
            seed: [Optional] a seed to give to the random number generator

        Returns:
            new_vector: an [x y z] vector with some error applied to it.
        """
        random.seed(seed)
        dropped_now = random.random() < self._dropout_chance_()

        if dropped_now:
            self.drops_in_a_row += 1
        else:
            self.drops_in_a_row = 0

        new_vector = (vector[0], vector[1], 0 if dropped_now else vector[2])
        return new_vector


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
