import os
import unittest

import trimesh

from echo_sound_sim import find_shallowest_depth, calculate_movement_vectors
from utils.cli_parsing import parse_args


class TestFindShallowestDepth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cwd = os.path.split(os.getcwd())[-1]
        if cwd == "tests":
            cls.mesh = trimesh.load(os.path.join(os.getcwd(), "test_data", "test_mesh.stl"))
        elif cwd == "echo_sounding_simulator":
            cls.mesh = trimesh.load(os.path.join(os.getcwd(), "tests", "test_data", "test_mesh.stl"))
        else:
            print(os.getcwd())
            raise EnvironmentError("Improper instantiation. Please run test from echo_sounding_simulator/ or"
                                   "echo_sounding_simulator/tests/")

    def test_point_with_one_face_returns_correct_depth(self):
        # 4 decimal places is considered adequate, as the mesh is in reference to the meter. Therefore, 3
        # decimal places gives us depth accuracy down to the millimeter
        self.assertAlmostEqual(-1.33613, find_shallowest_depth(self.mesh, 4.27498, -1.95354), places=3)

    def test_point_with_multiple_faces_returns_correct_depth(self):
        # 4 decimal places is considered adequate, as the mesh is in reference to the meter. Therefore, 3
        # decimal places gives us depth accuracy down to the millimeter
        self.assertAlmostEqual(0, find_shallowest_depth(self.mesh, 0, 0), places=3)

    def test_point_outside_of_bounds_returns_none(self):
        self.assertIsNone(find_shallowest_depth(self.mesh, 15, 7))


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


if __name__ == '__main__':
    unittest.main()
