def line_sign(point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]) -> float:
    """
    Calculates whether a point lies above or below a line between two points
    :param point: The point of interest [x y]
    :param line_start: One side of the line [x y]
    :param line_end: The other side of the line [x y]
    :return: Positive if above the line, negative if below
    """
    return ((point[0] - line_end[0]) * (line_start[1] - line_end[1]) -
            (line_start[0] - line_end[0]) * (point[1] - line_end[1]))


def point_in_tri(point: tuple[float, float], v1: tuple[float, float, float],
                 v2: tuple[float, float, float], v3: tuple[float, float, float]) -> bool:
    """
    Calculated whether an [x y] point is within the vertical slice of the triangular face
    created by the [x y z] verticies.
    :param point: [x y] point of interest
    :param v1: [x y z] vertex
    :param v2: [x y z] vertex
    :param v3: [x y z] vertex
    :return: a boolean of whether the point is withing the [x y] bound of the face
    """
    d1 = line_sign(point, v1[0:2], v2[0:2])
    d2 = line_sign(point, v2[0:2], v3[0:2])
    d3 = line_sign(point, v3[0:2], v1[0:2])

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_pos and has_neg)
