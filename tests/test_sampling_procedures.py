import unittest

import numpy as np

from utils.sampling_procedures import calculate_movement_vectors, \
    parallel_track_sampling_generator, drawn_path_sampling_generator
from utils.cli_parsing import parse_args


class TestCalculateMovementVectors(unittest.TestCase):
    def test_default_vector_is_a_change_in_one_meter(self):
        args = parse_args(['file.stl'])
        right, up = calculate_movement_vectors(args.sample_rate, args.velocity)

        self.assertEqual((1, 0), right)
        self.assertEqual((0, 1), up)

    def test_halving_the_sample_rate_doubles_the_distance_between_sample(self):
        sample_rate = 0.5
        velocity = 1
        right, up = calculate_movement_vectors(sample_rate, velocity)

        self.assertEqual((2, 0), right)
        self.assertEqual((0, 2), up)

    def test_halving_the_velocity_halves_the_distance_between_sample(self):
        sample_rate = 1
        velocity = 0.5
        right, up = calculate_movement_vectors(sample_rate, velocity)

        self.assertEqual((0.5, 0), right)
        self.assertEqual((0, 0.5), up)


class TestParallelTrackSamplingGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ten_meter_results = []

        for i in range(0, 10, 2):
            up_path = []
            down_path = []
            for j in range(10):
                up_path.append((i, j))
                down_path.insert(0, (i + 1, j))

            ten_meter_results.extend(up_path)
            ten_meter_results.extend(down_path)

        cls.ten_meter_results = ten_meter_results
        cls.ten_meter_balanced = [(p[0] - 5, p[1] - 5) for p in ten_meter_results]

    def test_default_movement_is_along_the_one_meter_grid(self):
        args = parse_args(['file.stl'])
        right, up = calculate_movement_vectors(args.sample_rate, args.velocity)

        results = list(parallel_track_sampling_generator(0, 9, 0, 9, right, up))

        self.assertEqual(len(results), len(self.ten_meter_results))
        for i in range(len(self.ten_meter_results)):
            self.assertTupleEqual(results[i], self.ten_meter_results[i])

    def test_extra_half_meter_per_axis_does_not_change_data(self):
        right, up = calculate_movement_vectors(1, 1)

        results = list(parallel_track_sampling_generator(0, 9.5, 0, 9.5, right, up))

        self.assertEqual(len(results), len(self.ten_meter_results))
        for i in range(len(self.ten_meter_results)):
            self.assertTupleEqual(results[i], self.ten_meter_results[i])

    def test_mix_of_positive_and_negative_coordinates_work_correctly(self):
        right, up = calculate_movement_vectors(1, 1)

        results = list(parallel_track_sampling_generator(-5, 4, -5, 4, right, up))

        self.assertEqual(len(results), len(self.ten_meter_balanced))
        for i in range(len(self.ten_meter_balanced)):
            self.assertTupleEqual(results[i], self.ten_meter_balanced[i])


class TestDrawnPathSamplingGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_rate = 1
        cls.velocity = 1

    def test_one_point_raises_assertion_error(self):
        # Setup
        provided_points = [(0, 0)]

        # Execute
        generator = drawn_path_sampling_generator(provided_points, self.sample_rate, self.velocity)

        # Assert
        with self.assertRaises(AssertionError):
            list(generator)

    def test_point_along_segment_with_positive_slope_yields_correctly(self):
        # Setup
        provided_points = [(0, 0), (8, 6)]
        expected_points = np.asarray([(4, 3), (8, 6)])

        # Execute
        generator = drawn_path_sampling_generator(provided_points, self.sample_rate, 5)
        actual_points = np.asarray(list(generator))

        # Assert
        self.assertTupleEqual(expected_points.shape, actual_points.shape)
        self.assertTrue(np.equal(expected_points, actual_points).all())

    def test_point_along_segment_with_negative_slope_yields_correctly(self):
        # Setup
        provided_points = [(0, 0), (8, -6)]
        expected_points = np.asarray([(4, -3), (8, -6)])

        # Execute
        generator = drawn_path_sampling_generator(provided_points, self.sample_rate, 5)
        actual_points = np.asarray(list(generator))

        # Assert
        self.assertTupleEqual(expected_points.shape, actual_points.shape)
        self.assertTrue(np.equal(expected_points, actual_points).all())

    def test_point_at_end_of_segment_yields_correctly(self):
        self.fail("not implemented")

    def test_point_past_one_segment_yields_correctly(self):
        self.fail("not implemented")

    def test_point_past_several_segments_yields_correctly(self):
        self.fail("not implemented")

    def test_multiple_points_yield_correctly(self):
        self.fail("not implemented")


if __name__ == '__main__':
    unittest.main()
