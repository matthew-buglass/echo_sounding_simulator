import sys
from trimesh import load, Trimesh

from utils.cli_parsing import parse_args


def triplane_intercept(verts: list, x: float, y:float):
    """
    Calculates the intercept of x and y projected onto the triangular plane created by the three vertices in verts.
    :param verts: a [3 3] array of x, y, and z position of three vertices that create a plane.
    :param x: the x point to be projected onto the plane
    :param y: the y point to be projected onto the plane
    :return: the z position of the projected points x and y
    """
    pass


def find_shallowest_depth(mesh: Trimesh, x: float, y:float):
    """
    Provide a tri mesh and an x and y position. Returns the shallowest depth (what and echo sounder would find)
    :param mesh: A Trimesh object
    :param x: a real x position
    :param y: a real y position
    :return: a real number that is the z position closest to 0
    """
    pass


if __name__ == '__main__':
    # Get cli arguments
    args = parse_args(sys.argv[1:])

    # Import data file
    mesh = load(args.data_file)
    min_x, min_y, min_z = mesh.bounds[0]
    max_x, max_y, max_z = mesh.bounds[1]

    print(f"Min Bounds {min_x} {min_y} {min_z}")
    print(f"Min Bounds {max_x} {max_y} {max_z}")
    print(f"Point samples {mesh.sample(3)}")
