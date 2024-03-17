import math
import unittest

import numpy as np

from utils.error_pipeline import ErrorType, Noise, run_pipeline, FalseBottom, Dropout
from utils.geometry import find_x_y_theta


class TestErrorType(unittest.TestCase):
    def test_instantiating_generic_raises_type_error(self):
        self.assertRaises(TypeError, ErrorType)

    def test_instantiating_incomplete_error_type_raises_type_error(self):
        class BadError(ErrorType):
            def __init__(self, *args, **kwargs):
                super().__init__(self, *args, **kwargs)

        self.assertRaises(TypeError, BadError)


class TestNoiseErrorType(unittest.TestCase):
    def test_calling_on_five_percent_error_calculates_vector_correctly(self):
        seeds = [0, 10, 304597]
        expected_vectors = [(0, 0, 1.0344421851525047), (0, 0, 1.0071402594689913), (0, 0, 0.9884574295419192)]
        err = Noise(0.05)
        vector = (0, 0, 1)

        for i, seed in enumerate(seeds):
            new_vector = err.eval(vector, seed)

            # vector is correct and error is within 5%
            self.assertTrue(abs(vector[2] - new_vector[2]) / vector[2] <= 0.05, msg="Error not within 5%")
            self.assertTupleEqual(new_vector, expected_vectors[i], msg="Vectors not equal")


class TestFalseBottomErrorType(unittest.TestCase):
    def test_default_debris_surface_area_is_10(self):
        expected_area = 10
        err = FalseBottom()
        err.init_debris(0, 0, 100, 100)

        (p1, p2, _), (_, p3, _) = err.debris_tris

        length = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
        width = ((p1[0] - p3[0]) ** 2 + (p1[1] - p3[1]) ** 2) ** 0.5
        actual_area = length * width

        self.assertAlmostEqual(actual_area, expected_area)

    def test_custom_debris_surface_area_is_correct(self):
        expected_area = 20
        err = FalseBottom(debris_size=expected_area)
        err.init_debris(0, 0, 100, 100)

        (p1, p2, _), (_, p3, _) = err.debris_tris

        length = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
        width = ((p1[0] - p3[0]) ** 2 + (p1[1] - p3[1]) ** 2) ** 0.5
        actual_area = length * width

        self.assertAlmostEqual(actual_area, expected_area)

    def test_debris_field_is_square(self):
        err = FalseBottom(seed=1)
        err.init_debris(0, 0, 100, 100)
        ninety_degrees = np.pi / 2
        length = err.length
        width = err.width
        hypotenuse = np.linalg.norm([err.width, err.length], 2)

        # Triangles that form the rectangle:
        #  P2 --- P4
        #  |      |
        #  |      |
        #  P1 --- P3
        (p1, p2, p4), (_, p3, _) = err.debris_tris

        # Distances
        p1_p2_dist = math.dist(p1, p2)
        p3_p4_dist = math.dist(p3, p4)
        p1_p3_dist = math.dist(p1, p3)
        p4_p2_dist = math.dist(p4, p2)
        p1_p4_dist = math.dist(p1, p4)
        p3_p2_dist = math.dist(p3, p2)

        self.assertAlmostEqual(length, p1_p2_dist)
        self.assertAlmostEqual(length, p3_p4_dist)
        self.assertAlmostEqual(width, p1_p3_dist)
        self.assertAlmostEqual(width, p4_p2_dist)
        self.assertAlmostEqual(hypotenuse, p1_p4_dist)
        self.assertAlmostEqual(hypotenuse, p3_p2_dist)

        # Angles
        p2_p1_p3_theta = find_x_y_theta(p2, p1, p3)
        p1_p3_p4_theta = find_x_y_theta(p1, p3, p4)
        p3_p4_p2_theta = find_x_y_theta(p3, p4, p2)
        p4_p2_p1_theta = find_x_y_theta(p4, p2, p1)

        self.assertAlmostEqual(p2_p1_p3_theta, ninety_degrees)
        self.assertAlmostEqual(p1_p3_p4_theta, ninety_degrees)
        self.assertAlmostEqual(p3_p4_p2_theta, ninety_degrees)
        self.assertAlmostEqual(p4_p2_p1_theta, ninety_degrees)

    def test_calling_eval_in_triangle_raises_incorrect_depth(self):
        expected_depth = 10
        points = [(14, 84, expected_depth * 2), (21, 84.8, 30), (18, 84.4, 10)]
        err = FalseBottom(seed=1)
        err.init_debris(0, 0, 100, 100)

        for p in points:
            new_p = err.eval(p)
            self.assertEqual(new_p[2], expected_depth)

    def test_calling_eval_outside_of_triangle_raises_correct_depth(self):
        points = [(12, 80, 15), (30, 75, 30), (20, 80, 10)]
        err = FalseBottom(seed=1)
        err.init_debris(0, 0, 100, 100)

        for p in points:
            new_p = err.eval(p)
            self.assertEqual(new_p[2], p[2])


class TestSensorDropout(unittest.TestCase):
    def test_no_dropout_causes_vector_to_remain_the_same(self):
        points = [(12, 80, 15), (30, 75, 30), (20, 80, 10)]
        err = Dropout(error_rate=0.1)

        for p in points:
            new_p = err.eval(p, seed=1)
            self.assertTupleEqual(new_p, p, msg="Vectors not equal")

    def test_dropout_causes_vector_z_to_be_zero(self):
        points = [(12, 80, 15), (30, 75, 30), (20, 80, 10)]
        expected_points = [(12, 80, 0), (30, 75, 0), (20, 80, 0)]
        err = Dropout(error_rate=0.9)

        for i, p in enumerate(points):
            new_p = err.eval(p, seed=10)
            self.assertTupleEqual(new_p, expected_points[i], msg="Vectors not equal")

    def test_dropout_increases_dropout_chance(self):
        point = (12, 80, 15)
        expected_point = (12, 80, 0)
        err = Dropout(error_rate=0.7, drop_off_rate=0.01)

        self.assertTupleEqual(err.eval(point, seed=10), expected_point)
        self.assertAlmostEqual(err._dropout_chance_(), 0.71)
        self.assertTupleEqual(err.eval(point, seed=10), expected_point)
        self.assertAlmostEqual(err._dropout_chance_(), 0.705)

    def test_dropout_causes_dropout_count_to_increment(self):
        point = (12, 80, 15)
        expected_point = (12, 80, 0)
        err = Dropout(error_rate=0.7, drop_off_rate=0.01)
        new_point = err.eval(point, seed=10)

        self.assertTupleEqual(new_point, expected_point)
        self.assertAlmostEqual(err.drops_in_a_row, 1)

    def test_no_dropout_resets_the_dropout_chance(self):
        point = (12, 80, 15)
        expected_point = (12, 80, 15)
        err = Dropout(error_rate=0.01, drop_off_rate=0.01)
        err.drops_in_a_row = 5

        self.assertEqual(err.drops_in_a_row, 5)
        new_point = err.eval(point, seed=10)
        self.assertTupleEqual(new_point, expected_point)
        self.assertAlmostEqual(err.drops_in_a_row, 0)


class TestRunPipeline(unittest.TestCase):
    def test_with_empty_pipeline_yields_identical_vector(self):
        errors = []
        start_vector = (0, 0, 1)
        expected_vector = (0.0, 0.0, 1.0)

        new_vector = run_pipeline(errors, start_vector)

        self.assertEqual(3, len(new_vector))
        self.assertAlmostEqual(expected_vector[0], new_vector[0])
        self.assertAlmostEqual(expected_vector[1], new_vector[1])
        self.assertAlmostEqual(expected_vector[2], new_vector[2])

    def test_with_one_noise_pipeline_step_yields_correct_vector(self):
        errors = [Noise(0.05)]
        seed = 304597
        start_vector = (0, 0, 1)
        expected_vector = (0.0, 0.0, 0.9884574295419192)

        new_vector = run_pipeline(errors, start_vector, seed=seed)

        self.assertEqual(3, len(new_vector))
        self.assertAlmostEqual(expected_vector[0], new_vector[0])
        self.assertAlmostEqual(expected_vector[1], new_vector[1])
        self.assertAlmostEqual(expected_vector[2], new_vector[2])

    def test_with_multiple_noise_pipeline_steps_yields_correct_vector(self):
        errors = [Noise(0.05), Noise(0.01), Noise(0.10)]
        seed = 1238987523
        start_vector = (0, 0, 1)
        expected_vector = (0.0, 0.0, 0.9670810794357534)

        new_vector = run_pipeline(errors, start_vector, seed=seed)

        self.assertEqual(3, len(new_vector))
        self.assertAlmostEqual(expected_vector[0], new_vector[0])
        self.assertAlmostEqual(expected_vector[1], new_vector[1])
        self.assertAlmostEqual(expected_vector[2], new_vector[2])


if __name__ == '__main__':
    unittest.main()
