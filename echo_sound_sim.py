import sys
from trimesh import load, Trimesh

from utils.cli_parsing import parse_args
from utils.geometry import point_in_tri, triangular_plane_intercept


def find_shallowest_depth(mesh: Trimesh, x: float, y:float):
    """
    Provide a tri mesh and an x and y position. Brute force algorithm that returns the shallowest depth
    (what and echo sounder would find)
    :param mesh: A Trimesh object
    :param x: a real x position
    :param y: a real y position
    :return: a real number that is the z position closest to 0
    """
    # Pick the lowest point in the mesh as our starting max
    max_z = mesh.bounds[0, 2]

    for i, face in enumerate(mesh.faces):
        v1 = mesh.vertices[face[0]]
        v2 = mesh.vertices[face[1]]
        v3 = mesh.vertices[face[2]]

        if point_in_tri((x, y), v1, v2, v3):
            z = triangular_plane_intercept(x, y, v1, v2, v3)
            if z > max_z:
                max_z = z

    return max_z


if __name__ == '__main__':
    # Get cli arguments
    args = parse_args(sys.argv[1:])

    # Import data file
    mesh = load(args.data_file)
    min_x, min_y, _ = mesh.bounds[0]
    max_x, max_y, _ = mesh.bounds[1]

    print(f"Min Bounds {min_x} {min_y}")
    print(f"Min Bounds {max_x} {max_y}")
    print(f"Point samples \n{mesh.sample(3)}")

    # find a face that contains a point
    print(f"z at origin {find_shallowest_depth(mesh, 0, 0)}")
