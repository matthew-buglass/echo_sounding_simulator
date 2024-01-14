import sys
import time

from trimesh import load

from utils.cli_parsing import parse_args
from utils.error_pipeline import run_pipeline
from utils.sampling_procedures import calculate_movement_vectors, find_shallowest_depth, \
    parallel_track_sampling_generator, process_position

if __name__ == '__main__':
    # Get cli arguments
    args = parse_args(sys.argv[1:])

    # Import data file
    mesh = load(args.data_file)

    # get movement parameters
    min_x, min_y, _ = mesh.bounds[0]
    max_x, max_y, _ = mesh.bounds[1]
    right, up = calculate_movement_vectors(args.sample_rate, args.velocity)

    # calculate wait time
    wait_secs = 1 / args.sample_rate

    # Run the sampling
    # for x, y in parallel_track_sampling_generator(min_x, max_x, min_y, max_y, right, up):
    #     new_vector, exec_time = process_position(mesh, x, y, args.errors)
    #     if new_vector is not None:
    #         print(new_vector)
    #     time.sleep(max(wait_secs - exec_time, 0))

    for x, y in parallel_track_sampling_generator(min_x, max_x, min_y, max_y, right, up):
        new_vector = process_position(mesh, x, y, args.errors)
        if new_vector is not None:
            print(new_vector)
        time.sleep(wait_secs)
