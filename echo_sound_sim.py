import sys
import time

import trimesh

from utils.cli_parsing import parse_args
from utils.mesh import CustomTriMesh
from utils.sampling_procedures import parallel_track_sampling_generator, process_position, \
    drawn_path_sampling_generator

if __name__ == '__main__':
    # Get cli arguments
    args = parse_args(sys.argv[1:])

    # Import data file
    mesh = CustomTriMesh(trimesh.load(args.data_file))

    # get movement parameters
    min_x, min_y, _ = mesh.bounds[0]
    max_x, max_y, _ = mesh.bounds[1]
    path_generator_kwargs = {
        # General
        "velocity": args.velocity,
        "sample_rate": args.sample_rate,
        # Parallel Track
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
    }

    if args.path_type == "drawn":
        path_points = mesh.get_path_over_mesh()
        path_generator = drawn_path_sampling_generator(
            path_coords=path_points, velocity=args.velocity, sample_rate=args.sample_rate
        )
    elif args.path_type == "parallel":
        path_generator = parallel_track_sampling_generator(
            min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y, velocity=args.velocity, sample_rate=args.sample_rate
        )

    # calculate wait time
    wait = not args.no_wait
    if wait:
        wait_secs = 1 / args.sample_rate
    else:
        wait_secs = 0

    # Run the sampling
    emitter = args.emitter_type
    for x, y in path_generator:
        t1 = time.time()
        new_vector = process_position(mesh, x, y, args.errors)
        if new_vector is not None:
            emitter.emit_vector(new_vector)
            t2 = time.time()
            time.sleep(max(wait_secs - (t2 - t1), 0))
