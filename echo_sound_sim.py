import sys
import time

import trimesh

from utils.cli_parsing import parse_args
from utils.error_pipeline import FalseBottom
from utils.mesh import CustomTriMesh
from utils.sampling_procedures import parallel_track_sampling_generator, process_position, \
    drawn_path_sampling_generator


def run_sampling(path, wait_secs, side_effect=None) -> None:
    """
    Takes an iterator the yields x and y coordinates and runs a sampling path
    Args:
        path (iterator): an iterator the yields x and y coordinates
        wait_secs (float): a number of seconds to wait between samples
        side_effect (callable): a function that takes a vector that we want to have as
            a side effect of the path sampling

    Returns:
        None
    """
    for x, y in path:
        t1 = time.time()
        new_vector = process_position(mesh, x, y, args.errors)
        if new_vector is not None:
            emitter.emit_vector(new_vector)

            if side_effect:
                side_effect(new_vector)

            t2 = time.time()
            time.sleep(max(wait_secs - (t2 - t1), 0))


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

    # Perform any additional setup for the error pipeline
    for err in args.errors:
        if isinstance(err, FalseBottom):
            err.init_debris(min_x, min_y, max_x, max_y)

    # calculate wait time
    wait = not args.no_wait
    if wait:
        wait_secs = 1 / args.sample_rate
    else:
        wait_secs = 0

    emitter = args.emitter_type
    while True:
        # Get the Sampling Path Type
        if args.path_type == "drawn":
            path_points = mesh.get_path_over_mesh()
            # Exit if we don't get a path
            if len(path_points) == 0:
                print("No Path received")
                sys.exit(0)

            path_generator = drawn_path_sampling_generator(
                path_coords=path_points, velocity=args.velocity, sample_rate=args.sample_rate
            )
            run_sampling(path=path_generator, wait_secs=wait_secs, side_effect=mesh.add_depth_reading)
        elif args.path_type == "parallel":
            path_generator = parallel_track_sampling_generator(
                min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y, velocity=args.velocity, sample_rate=args.sample_rate
            )
            run_sampling(path_generator, wait_secs)
            # exit after the pass
            sys.exit(0)
