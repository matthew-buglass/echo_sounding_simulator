import sys
import time

from trimesh import load

from utils.cli_parsing import parse_args
from utils.sampling_procedures import calculate_movement_vectors, parallel_track_sampling_generator, process_position

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
    emitter = args.emitter_type
    for x, y in parallel_track_sampling_generator(min_x, max_x, min_y, max_y, right, up):
        t1 = time.time()
        new_vector, exec_time = process_position(mesh, x, y, args.errors)
        if new_vector is not None:
            emitter.emit_vector(new_vector)
            t2 = time.time()
            time.sleep(max(wait_secs - (t2 - t1), 0))
