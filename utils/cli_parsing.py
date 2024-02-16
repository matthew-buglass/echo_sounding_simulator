import argparse

from utils.emitters import StdOutVectorEmitter
from utils.error_pipeline import Noise


class ParseErrorPipeline(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        for val in values:
            err_type, err_val = val.split("@")
            match err_type:
                case "noise":
                    items.append(Noise(float(err_val)))
                case _:
                    pass

        setattr(namespace, self.dest, items)


class ParseVectorEmitter(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        match values:
            case "file":
                item = StdOutVectorEmitter()
            case "endpoint":
                item = StdOutVectorEmitter()
            case "stdout":
                item = StdOutVectorEmitter()
            case _:
                item = StdOutVectorEmitter()

        setattr(namespace, self.dest, item)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file",
                        help="An 3D data file to represent the surface to sample")
    parser.add_argument("-em",
                        "--emitter_type",
                        action=ParseVectorEmitter,
                        help="Where you want to emit the result vectors.",
                        choices=["stdout", "file", "endpoint"],
                        default=StdOutVectorEmitter())
    parser.add_argument("-sr",
                        "--sample_rate",
                        help="The rate (in Hertz) at which to sample the surface. Defaults to 1hz.",
                        type=float,
                        default=1.0)
    parser.add_argument("-e",
                        "--errors",
                        action=ParseErrorPipeline,
                        nargs="+",
                        help="A list describing the error introduction pipeline. Current formats:\n"
                             "\tnoise@0.05 - A random percent of noise present in a sensor. Plus or minus the value.",
                        default=[])
    parser.add_argument("-vel",
                        "--velocity",
                        type=float,
                        default=1,
                        help="The velocity of the research vessel in m/s. Defaults to 1 m/s (3.6 km/hr)")
    return parser.parse_args(args)
