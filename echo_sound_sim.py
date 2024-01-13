import sys
from trimesh import load

from utils.cli_parsing import parse_args
from utils.sampling_procedures import calculate_movement_vectors, find_shallowest_depth


if __name__ == '__main__':
    # Get cli arguments
    args = parse_args(sys.argv[1:])

    # Import data file
    mesh = load(args.data_file)

    # get movement parameters
    min_x, min_y, _ = mesh.bounds[0]
    max_x, max_y, _ = mesh.bounds[1]
    right, up = calculate_movement_vectors(args.sample_rate, args.velocity)
    position = (min_x, min_y)

    # calculate wait time
    wait_time = 1 / args.sample_rate

    print(f"Min Bounds {min_x} {min_y}")
    print(f"Min Bounds {max_x} {max_y}")
    print(f"Point samples \n{mesh.sample(3)}")

    # find a face that contains a point
    print(f"z at origin {find_shallowest_depth(mesh, 0, 0)}")
