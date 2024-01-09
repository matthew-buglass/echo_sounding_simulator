import argparse
import re


class ValidateObjectFile(argparse.Action):
    file_regex = re.compile(".*\.stl")

    def __call__(self, parser, namespace, values, option_string=None):
        if not re.match(self.file_regex, values):
            parser.error(f"An stl data file is required. Received {values}")
        setattr(namespace, self.dest, values)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("stl_file",
                        help="An stl file to represent the surface to sample",
                        action=ValidateObjectFile)
    parser.add_argument("--sample_rate",
                        help="The rate (in Hertz) at which to sample the surface. Defaults to 1hz.",
                        default=1)
    parser.add_argument("--sensor-error",
                        help="The z error rate of the sensor's readings. Defaults to 0.05.",
                        default=0.05)
    return parser.parse_args(args)
