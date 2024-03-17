import os
import unittest

import numpy as np
import trimesh

from utils.mesh import CustomTriMesh


class TestMesh(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cwd = os.path.split(os.getcwd())[-1]
        if cwd == "tests":
            cls.mesh = CustomTriMesh(trimesh.load(os.path.join(os.getcwd(), "test_data", "test_mesh.stl")))
        elif cwd == "echo_sounding_simulator":
            cls.mesh = CustomTriMesh(trimesh.load(os.path.join(os.getcwd(), "tests", "test_data", "test_mesh.stl")))
        else:
            print(os.getcwd())
            raise EnvironmentError("Improper instantiation. Please run test from echo_sounding_simulator/ or"
                                   "echo_sounding_simulator/tests/")

    def test_point_with_one_face_returns_correct_depth(self):
        # 4 decimal places is considered adequate, as the mesh is in reference to the meter. Therefore, 3
        # decimal places gives us depth accuracy down to the millimeter
        self.assertAlmostEqual(-1.33613, self.mesh.get_shallowest_depth(4.27498, -1.95354), places=3)

    def test_point_with_multiple_faces_returns_correct_depth(self):
        # 4 decimal places is considered adequate, as the mesh is in reference to the meter. Therefore, 3
        # decimal places gives us depth accuracy down to the millimeter
        self.assertAlmostEqual(0, self.mesh.get_shallowest_depth(0, 0), places=3)

    def test_point_outside_of_bounds_returns_none(self):
        self.assertIsNone(self.mesh.get_shallowest_depth(15, 7))

    def test_image_to_cartesian_coordinates_are_correct(self):
        # Setup
        self.mesh.image_coords = [
            (0, 0),
            (self.mesh.img_width, 0),
            (self.mesh.img_height, self.mesh.img_width),
            (0, self.mesh.img_height)
        ]
        expected_coords = np.asarray([
            (-10, 10),
            (10, 10),
            (10, -10),
            (-10, -10)
        ])

        # Execute
        actual_coords = np.asarray(self.mesh._process_out_coordinates_())

        # Assert
        self.assertTupleEqual(expected_coords.shape, actual_coords.shape)
        self.assertTrue(np.equal(expected_coords, actual_coords).all())

    def test_x_coordinate_conversion_is_correct(self):
        expected_coords = [13.4375, -10.0, 65.15625, 38.671875, 32.890625]
        expected_image_idxs = [300, 0, 962, 623, 549]

        for i, expected_coord in enumerate(expected_coords):
            expected_image_idx = expected_image_idxs[i]
            actual_coord = self.mesh._x_image_index_to_coordinate_display(expected_image_idx)
            actual_image_idx = self.mesh._x_coordinate_display_to_image_index(expected_coord)

            self.assertAlmostEqual(actual_coord, expected_coord)
            self.assertEqual(actual_image_idx, expected_image_idx)

    def test_y_coordinate_conversion_is_correct(self):
        expected_coords = [7.734375, -17.03125, -47.65625, 10.0, -66.5625]
        expected_image_idxs = [29, 346, 738, 0, 980]

        for i, expected_coord in enumerate(expected_coords):
            expected_image_idx = expected_image_idxs[i]
            actual_coord = self.mesh._y_image_index_to_coordinate_display(expected_image_idx)
            actual_image_idx = self.mesh._y_coordinate_display_to_image_index(expected_coord)

            self.assertAlmostEqual(actual_coord, expected_coord)
            self.assertEqual(actual_image_idx, expected_image_idx)


if __name__ == '__main__':
    unittest.main()
