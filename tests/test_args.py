import unittest

from utils.cli_parsing import parse_args
from utils.error_pipeline import Noise


class TestArgumentParsing(unittest.TestCase):
    def test_no_file_provided_causes_system_exit(self):
        args = []
        self.assertRaises(SystemExit, parse_args, args)

    def test_only_file_does_not_crash_and_has_all_arguments(self):
        args = ["test.stl"]
        arg_space = parse_args(args)

        self.assertSetEqual(set(arg_space.__dict__.keys()), {"errors", "sample_rate", "data_file", "velocity"})
        self.assertEqual(arg_space.errors, [])
        self.assertEqual(arg_space.sample_rate, 1)
        self.assertEqual(arg_space.data_file, "test.stl")
        self.assertEqual(arg_space.velocity, 1)

    def test_custom_sample_rate(self):
        args1 = ["test.stl", "--sample_rate=5"]
        args2 = ["test.stl", "-sr=0.1"]

        arg_space1 = parse_args(args1)
        arg_space2 = parse_args(args2)

        self.assertEqual(arg_space1.sample_rate, 5.0)
        self.assertEqual(arg_space2.sample_rate, 0.1)

    def test_one_noise_within_range(self):
        args1 = ["test.stl", "--errors", "noise@0.05"]
        args2 = ["test.stl", "-e", "noise@0.1"]

        arg_space1 = parse_args(args1)
        arg_space2 = parse_args(args2)

        self.assertEqual(arg_space1.errors, [Noise(0.05)])
        self.assertEqual(arg_space2.errors, [Noise(0.1)])

    def test_noise_bigger_than_one_causes_system_exit(self):
        args1 = ["test.stl", "--errors", "noise@1.001"]
        args2 = ["test.stl", "-e", "noise@1.5"]

        self.assertRaises(ValueError, parse_args, args1)
        self.assertRaises(ValueError, parse_args, args2)

    def test_noise_smaller_than_zero_causes_system_exit(self):
        args1 = ["test.stl", "--errors", "noise@-0.5"]
        args2 = ["test.stl", "-e", "noise@-6"]

        self.assertRaises(ValueError, parse_args, args1)
        self.assertRaises(ValueError, parse_args, args2)

    def test_noise_at_one_and_zero_are_valid(self):
        args1 = ["test.stl", "--errors", "noise@0"]
        args2 = ["test.stl", "-e", "noise@1"]

        arg_space1 = parse_args(args1)
        arg_space2 = parse_args(args2)

        self.assertEqual(arg_space1.errors, [Noise(0)])
        self.assertEqual(arg_space2.errors, [Noise(1)])

    def test_multiple_noises(self):
        args1 = ["test.stl", "--errors", "noise@0.05", "noise@0.1", "noise@0.01"]
        args2 = ["test.stl", "-e", "noise@0.1", "noise@0.006", "-sr=0.1", "--errors", "noise@0.9"]

        arg_space1 = parse_args(args1)
        arg_space2 = parse_args(args2)

        self.assertEqual(arg_space1.errors, [Noise(0.05), Noise(0.1), Noise(0.01)])
        self.assertEqual(arg_space2.errors, [Noise(0.1), Noise(0.006), Noise(0.9)])

    def test_custom_velocity(self):
        args1 = ["test.stl", "--velocity=5"]
        args2 = ["test.stl", "-vel=0.1"]

        arg_space1 = parse_args(args1)
        arg_space2 = parse_args(args2)

        self.assertEqual(arg_space1.velocity, 5.0)
        self.assertEqual(arg_space2.velocity, 0.1)


if __name__ == '__main__':
    unittest.main()
