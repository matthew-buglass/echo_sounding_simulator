import argparse

from utils.emitters import StdOutVectorEmitter, CsvVectorEmitter, TsvVectorEmitter, EndpointVectorEmitter
from utils.error_pipeline import Noise
from utils.sampling_procedures import parallel_track_sampling_generator, drawn_path_sampling_generator


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
    def __call__(self, parser, namespace, values, option_string=None):
        emitter, location = values.split("@")
        match emitter:
            case "csv":
                item = CsvVectorEmitter(location)
            case "tsv":
                item = TsvVectorEmitter(location)
            case "endpoint":
                item = EndpointVectorEmitter(location)
            case _:
                item = StdOutVectorEmitter()

        setattr(namespace, self.dest, item)


class ParsePathGenerator(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        match values:
            case "drawn":
                item = drawn_path_sampling_generator
            case _:
                item = parallel_track_sampling_generator

        setattr(namespace, self.dest, item)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file",
                        help="An 3D data file to represent the surface to sample")
    parser.add_argument("-p",
                        "--path_type",
                        action=ParseVectorEmitter,
                        help="The type of search pattern to use over the mesh",
                        choices=["parallel", "drawn"],
                        default=parallel_track_sampling_generator)
    parser.add_argument("-em",
                        "--emitter_type",
                        action=ParseVectorEmitter,
                        help="Where you want to emit the result vectors, if not to stdout.\n"
                             "Your choices are: csv@<filename>, tsv@<filename>, endpoint@<url>",
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
    parser.add_argument("--no-wait",
                        action="store_true",
                        help="Flag to disable the waiting part off the simulation. If given, the sampling rate "
                             "will remain the same, but the wait time between samples will be disabled.")
    return parser.parse_args(args)
