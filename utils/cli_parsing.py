import argparse


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file",
                        help="An 3D data file to represent the surface to sample")
    parser.add_argument("-sr",
                        "--sample_rate",
                        help="The rate (in Hertz) at which to sample the surface. Defaults to 1hz.",
                        type=float,
                        default=1.0)
    parser.add_argument("-e",
                        "--errors",
                        action='append',
                        help="A list describing the error introduction pipeline. Current formats:\n"
                             "\tnoise=0.05 - A random percent of noise present in a sensor. Plus or minus half the value.")
    return parser.parse_args(args)
