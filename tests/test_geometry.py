import unittest

from utils.geometry import line_sign, point_in_tri, triangular_plane_intercept


class TestLineSign(unittest.TestCase):
    def test_positive_above_x_axis(self):
        self.assertTrue(0 < line_sign((0, 1), (-2, 0), (5, 0)))

    def test_negative_below_x_axis(self):
        self.assertTrue(0 > line_sign((0, -1), (-2, 0), (5, 0)))

    def test_positive_when_above_arbitrary_line(self):
        self.assertTrue(0 < line_sign((-5, 5), (0, -3), (1.5, 0)))

    def test_negative_when_below_arbitrary_line(self):
        self.assertTrue(0 > line_sign((10, 3), (0, -3), (1.5, 0)))

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


class TestTriangularPlaneIntercept(unittest.TestCase):
    def setUp(self):
        self.v1 = (1, 2, 3)
        self.v2 = (1, 0, 1)
        self.v3 = (-2, 1, 0)

    def test_x_and_y_are_in_bounds(self):
        self.assertAlmostEquals(1/3, triangular_plane_intercept(0, 0, self.v1, self.v2, self.v3))

    def test_x_and_y_are_out_of_bounds(self):
        self.assertEqual(3, triangular_plane_intercept(7, -2, self.v1, self.v2, self.v3))


if __name__ == '__main__':
    unittest.main()
