import numpy as np


def line_sign(point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]) -> float:
    """
    Calculates whether a point lies above or below a line between two points

    Args:
        point: The point of interest [x y]
        line_start: One side of the line [x y]
        line_end: The other side of the line [x y]

    Returns:
        sign: 1 if above the line, -1 if below, 0 if on the line
    """
    res = (point[0] - line_end[0]) * (line_start[1] - line_end[1]) - (line_start[0] - line_end[0]) * (point[1] - line_end[1])
    if res == 0:
        return 0
    else:
        return int(res // abs(res))


def point_in_tri(point: tuple[float, float], v1: tuple[float, float, float],
                 v2: tuple[float, float, float], v3: tuple[float, float, float]) -> bool:
    """
    Calculated whether an [x y] point is within the vertical slice of the triangular face
    created by the [x y z] vertices.

    Args:
        point (tuple[float, float]): point of interest
        v1: [x y z] vector
        v2: [x y z] vector
        v3: [x y z] vector

    Returns:
        in_tri: a boolean of whether the point is withing the [x y] bound of the face
    """
    d1 = line_sign(point, v1[0:2], v2[0:2])
    d2 = line_sign(point, v2[0:2], v3[0:2])
    d3 = line_sign(point, v3[0:2], v1[0:2])

    # if the face has 3 identical points
    if d1 == d2 == d3 == 0:
        return point[0] == v1[0] and point[1] == v1[1]
    else:
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_pos and has_neg)


def triangular_plane_intercept(
        x: float,
        y: float,
        v1: tuple[float, float, float],
        v2: tuple[float, float, float],
        v3: tuple[float, float, float]
) -> float:
    """
    Calculates the z value of a point with coordinates [x y] on the plane defined by v1, v2, and v3.

    Args:
        x: the x point to be projected onto the plane
        y: the y point to be projected onto the plane
        v1: [x y z] vertex
        v2: [x y z] vertex
        v3: [x y z] vertex

    Returns:
        z: the z position of the projected points x and y
    """
    vector1 = np.subtract(v1, v2)
    vector2 = np.subtract(v1, v3)

    # Find the coefficients and the intercept of the equation of the plane
    coef = np.cross(vector1, vector2)
    intercept = np.dot(coef, v1)

    # Calculate z
    z = (intercept - (coef[0] * x + coef[1] * y)) / coef[2]
    return z


def get_x_y_rotated_vector(vector: np.ndarray, theta: float) -> np.ndarray:
    """
    Rotates a vector by theta about the origin
    Args:
        vector: a numpy array representation of a vector [x y]
        theta: the angle, in radians to rotate by

    Returns:
        rotated_vector: the vector rotated about the [x y] origin
    """
    R = np.asarray([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
    rotated_vector = np.dot(R, np.atleast_2d(vector).T)
    return np.atleast_1d(rotated_vector).T[0]


def find_x_y_theta(
        p1: tuple[float, float, float],
        p2: tuple[float, float, float],
        p3: tuple[float, float, float]
) -> float:
    """
    Finds the absolute angle (in radians) of intercept of the lines that pass through p1-p2 and p2-p3, intercepting at
    v2.
    Args:
        p1: an endpoint in the angle
        p2: The intercept point
        p3: an endpoint in the angle

    Returns:
        The radians angle, theta, between p1-p2-p3
    """
    v1 = np.asarray(p1[0:2]) - np.asarray(p2[0:2])
    v2 = np.asarray(p3[0:2]) - np.asarray(p2[0:2])

    abs_v1 = np.linalg.norm(v1, 2)
    abs_v2 = np.linalg.norm(v2, 2)

    theta = np.arccos(np.dot(v1, v2) / (abs_v1 * abs_v2))
    return theta
