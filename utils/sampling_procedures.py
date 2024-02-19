import numpy as np

from utils.error_pipeline import run_pipeline
from utils.geometry import triangular_plane_intercept
from utils.mesh import CustomTriMesh
from utils.timing import timed


def calculate_movement_vectors(sample_rate: float, velocity: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Returns the [x y] movement vector to apply to the ship's position at each sampling.

    Args:
        sample_rate: The rate in hertz that we are sampling at
        velocity: The velocity of the vessel in m/s

    Returns:
        [right up]: Two vectors [right up] where right moves the ship positively in the x direction and up moves the ship
    positively in the y direction
    """
    factor = velocity / sample_rate
    right = (1 * factor, 0)
    up = (0, 1 * factor)

    return right, up


def parallel_track_sampling_generator(min_x: float, max_x: float, min_y: float, max_y: float,
                                      right: tuple[float, float], up: tuple[float, float]) -> tuple[float, float]:
    """
    Simulates a zig-zag sampling pattern from the bottom left of the mesh to the top right of a bounding box between the
    points [min_x, min_y] to [max_x max_y]

    Args:
        min_x: The smallest x position of the mesh
        max_x: The largest x position of the mesh
        min_y: The smallest y position of the mesh
        max_y: The largest y position of the mesh
        right: The vector for moving to the right
        up: The vector for moving up

    Returns:
        [x y]: Successive [x y] positions
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


@timed
def process_position(mesh, x, y, error_pipeline):
    z = mesh.get_shallowest_depth(x, y)
    if z is not None:
        return run_pipeline(error_pipeline, (x, y, z))
    return None
