import numpy as np

from utils.error_pipeline import run_pipeline
from utils.timing import timed

def calculate_step_value(sample_rate: float, velocity: float) -> float:
    """
    Calculates the distance traveled for every sample step
    Args:
        sample_rate: The rate in hertz that we are sampling at
        velocity: The velocity of the vessel in m/s

    Returns:
        The distance traveled per step
    """
    return velocity / sample_rate


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
    step_size = calculate_step_value(sample_rate, velocity)
    right = (1 * step_size, 0)
    up = (0, 1 * step_size)

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

    Yields:
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


def drawn_path_sampling_generator(path_coords: list[tuple[float, float]], sample_rate: float, velocity: float):
    """
    Generates a series of sample points along a provided path generated by the provided coordinate given that the
    vessel is traveling at a constant velocity and sensor has a constant sample_rate

    Args:
        path_coords: A series of x, y coordinates forming an arbitrary path
        sample_rate: The rate in hertz that we are sampling at
        velocity: The velocity of the vessel in m/s

    Yields:
        [x y]: Successive [x y] positions
    """
    assert len(path_coords) >= 2, "A path must have at least two co-ordinates"

    step_distance = calculate_step_value(sample_rate, velocity)
    pos = np.asarray(path_coords[0])
    next_step_idx = 1

    while next_step_idx < len(path_coords):
        yield pos[0], pos[1]

        # find the next position be walking step_distance along the path
        dist_to_travel = step_distance

        while dist_to_travel > 0 and next_step_idx < len(path_coords):
            next_step = np.asarray(path_coords[next_step_idx])
            dist_to_next_point = np.linalg.norm(pos - next_step)

            # If the distance remaining in this segment is smaller than the distance we need to travel
            if dist_to_next_point < dist_to_travel:
                dist_to_travel = dist_to_travel - dist_to_next_point
                pos = next_step
                next_step_idx += 1
            # If the distance to the end current segment is the same as the distance we need to travel
            elif dist_to_next_point == dist_to_travel:
                dist_to_travel = 0
                pos = next_step
                next_step_idx += 1
                if next_step_idx == len(path_coords):
                    yield pos[0], pos[1]
            # If the distance we need to travel lands us in the middle of the current segment
            elif dist_to_next_point > dist_to_travel:
                slope = (pos[1] - next_step[1]) / (pos[0] - next_step[0])
                theta = np.arctan(slope)
                direction_array = np.asarray([np.sign(next_step[0] - pos[0]), np.sign(next_step[1] - pos[1])])

                if slope > 0:
                    movement_vector = abs(np.asarray([np.cos(theta) * dist_to_travel, np.sin(theta) * dist_to_travel]))
                else:
                    movement_vector = abs(np.asarray([np.cos(theta) * dist_to_travel, np.sin(theta) * dist_to_travel]))

                pos = pos + direction_array * movement_vector
                dist_to_travel = 0


@timed
def process_position(mesh, x, y, error_pipeline):
    z = mesh.get_shallowest_depth(x, y)
    if z is not None:
        return run_pipeline(error_pipeline, (x, y, z))
    return None
