import unittest

import numpy as np

from utils.geometry import line_sign, point_in_tri, triangular_plane_intercept, find_x_y_theta, get_x_y_rotated_vector


class TestLineSign(unittest.TestCase):
    def test_positive_above_x_axis(self):
        self.assertEqual(1, line_sign((0, 1), (-2, 0), (5, 0)))

    def test_negative_below_x_axis(self):
        self.assertEqual(-1, line_sign((0, -1), (-2, 0), (5, 0)))

    def test_positive_when_above_arbitrary_line(self):
        self.assertEqual(1, line_sign((-5, 5), (0, -3), (1.5, 0)))

    def test_negative_when_below_arbitrary_line(self):
        self.assertEqual(-1, line_sign((10, 3), (0, -3), (1.5, 0)))

    def test_zero_when_on_line_is(self):
        self.assertEqual(0, line_sign((5, 7), (0, -3), (1.5, 0)))


class TestInTriangle(unittest.TestCase):
    def setUp(self):
        self.v1 = (0, 2, 15)
        self.v2 = (1.5, 0.2, -6)
        self.v3 = (-1, -0.5, 0)

    def test_point_is_in_triangle_is_success(self):
        self.assertTrue(point_in_tri((0.5, 0.5), self.v1, self.v2, self.v3))

    def test_on_triangle_edge_succeeds(self):
        self.assertTrue(point_in_tri((0.5, 1.4), self.v1, self.v2, self.v3))

    def test_on_triangle_vertex_succeeds(self):
        self.assertTrue(point_in_tri(self.v1[0:2], self.v1, self.v2, self.v3))

    def test_below_triangle_fails(self):
        self.assertFalse(point_in_tri((0.5, -0.5), self.v1, self.v2, self.v3))

    def test_above_right_triangle_fails(self):
        self.assertFalse(point_in_tri((0.5, 2.5), self.v1, self.v2, self.v3))

    def test_above_left_triangle_fails(self):
        self.assertFalse(point_in_tri((-0.5, 1), self.v1, self.v2, self.v3))

    def test_point_only_valid_when_all_three_vertices_are_the_same_when_point_is_identical_to_vertices(self):
        self.assertTrue(point_in_tri(self.v1[0:2], self.v1, self.v1, self.v1))
        self.assertFalse(point_in_tri(self.v2[0:2], self.v1, self.v1, self.v1))


class TestTriangularPlaneIntercept(unittest.TestCase):
    def setUp(self):
        self.v1 = (1, 2, 3)
        self.v2 = (1, 0, 1)
        self.v3 = (-2, 1, 0)

    def test_x_and_y_are_in_bounds(self):
        self.assertAlmostEqual(1 / 3, triangular_plane_intercept(0, 0, self.v1, self.v2, self.v3))

    def test_x_and_y_are_out_of_bounds(self):
        self.assertEqual(3, triangular_plane_intercept(7, -2, self.v1, self.v2, self.v3))


class TestFindTheta(unittest.TestCase):
    def test_ninety_degree_works(self):
        expected_theta = np.pi / 2
        p1 = (0, 1, 10)
        p2 = (0, 0, 10)
        p3 = (1, 0, 10)

        actual_theta = find_x_y_theta(p1, p2, p3)

        self.assertAlmostEqual(actual_theta, expected_theta)

    def test_one_hundred_and_eighty_degree_works(self):
        expected_theta = np.pi
        p1 = (0, 1, 10)
        p2 = (0, 0, 10)
        p3 = (0, -1, 10)

        actual_theta = find_x_y_theta(p1, p2, p3)

        self.assertAlmostEqual(actual_theta, expected_theta)


class TestVectorRotation(unittest.TestCase):
    def test_rotating_ninety_degrees(self):
        expected_theta = np.pi / 2
        og_vector = (1, 0, 10)
        expected_vector = (0, 1, 10)
        err_range = 1e-100000

        actual_vector = get_x_y_rotated_vector(np.asarray(og_vector[0:2]), expected_theta)
        actual_vector = (float(actual_vector[0]), float(actual_vector[1]), 10)
        actual_theta = find_x_y_theta(og_vector, (0, 0, 0), actual_vector)

        self.assertAlmostEqual(actual_theta, expected_theta)
        self.assertTrue(
            all([expected_vector[i] - err_range <= c <= expected_vector[i] + err_range
                 for i, c in enumerate(actual_vector)]))


if __name__ == '__main__':
    unittest.main()
