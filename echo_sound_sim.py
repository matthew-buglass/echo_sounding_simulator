import sys
import numpy as np
from trimesh import load, Trimesh

from utils.cli_parsing import parse_args


def triplane_intercept(mesh: Trimesh, face_index: int, x: float, y:float):
    """
    Calculates the intercept of a vertical line at x and y onto the triangular plane at the face index.
    :param face_index: The index of the face to find the intersection
    :param mesh: A Trimesh object
    :param x: the x point to be projected onto the plane
    :param y: the y point to be projected onto the plane
    :return: the z position of the projected points x and y
    """
    # # pull triangles into the form of an origin + 2 vectors
    # tri_origins = mesh.vertices[mesh.faces[:, 0]]
    # tri_vectors = mesh.vertices[mesh.faces[:, 1:]].copy()
    # tri_vectors -= np.tile(tri_origins, (1, 2)).reshape((-1, 2, 3))
    #
    # # pull the vectors for the faces we are going to sample from
    # tri_origins = tri_origins[face_index]
    # tri_vectors = tri_vectors[face_index]


def find_shallowest_depth(mesh: Trimesh, x: float, y:float):
    """
    Provide a tri mesh and an x and y position. Brute force algorithm that returns the shallowest depth
    (what and echo sounder would find)
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
