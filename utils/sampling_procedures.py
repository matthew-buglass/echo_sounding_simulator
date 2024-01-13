import numpy as np
from trimesh import Trimesh

from utils.geometry import point_in_tri, triangular_plane_intercept


def calculate_movement_vectors(sample_rate: float, velocity: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Returns the [x y] movement vector to apply to the ship's position at each sampling.
    :param sample_rate: The rate in hertz that we are sampling at
    :param velocity: The velocity of the vessel in m/s
    :return: Two vectors [right up] where right moves the ship positively in the x direction and up moves the ship
    positively in the y direction
    """
    factor = velocity / sample_rate
    right = (1 * factor, 0)
    up = (0, 1 * factor)

    return right, up


def find_shallowest_depth(mesh: Trimesh, x: float, y: float):
    """
    Provide a tri mesh and an x and y position. Brute force algorithm that returns the shallowest depth
    (what and echo sounder would find)
    :param mesh: A Trimesh object
    :param x: a real x position
    :param y: a real y position
    :return: a real number that is the maximum (shallowest) z position, or None if the specified point is
        outside the mesh
    """
    # Pick the lowest point in the mesh as our starting max
    max_z = None

    for i, face in enumerate(mesh.faces):
        v1 = mesh.vertices[face[0]]
        v2 = mesh.vertices[face[1]]
        v3 = mesh.vertices[face[2]]

        if point_in_tri((x, y), v1, v2, v3):
            z = triangular_plane_intercept(x, y, v1, v2, v3)
            if max_z is None or z > max_z:
                max_z = z

    return max_z


def parallel_track_sampling_generator(min_x: float, max_x: float, min_y: float, max_y: float,
                                      right: tuple[float, float], up: tuple[float, float]):
    """
    Simulates a zig-zag sampling pattern from the bottom left of the mesh to the top right of a bounding box between the
    points [min_x, min_y] to [max_x max_y]
    :param min_x: The smallest x position of the mesh
    :param max_x: The largest x position of the mesh
    :param min_y: The smallest y position of the mesh
    :param max_y: The largest y position of the mesh
    :param right: The vector for moving to the right
    :param up: The vector for moving up
    :returns: Successive [x y] positions
    """
    pos = np.array([min_x, min_y])

    # These control the direction, positive is up/right and negative is down/left
    y_factor = 1

    while pos[0] <= max_x and pos[1] <= max_y:
        yield pos[0], pos[1]

        # try to go up or down
        pos = np.add(pos, np.multiply(y_factor, up))

        # if moving up or down would put us outside the mesh
        if not min_y <= pos[1] <= max_y:
            # Change directions, go back, and move right
            y_factor = -1 * y_factor
            pos = np.add(pos, np.multiply(y_factor, up))
            pos = np.add(pos, right)
