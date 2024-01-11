"""Main module and script for running the echo sounding simulator. Use python echo_sound_sim.py --help for more
details"""
import sys

from utils.cli_parsing import parse_args

if __name__ == '__main__':
    # Get cli arguments
    print(parse_args(sys.argv[1:]))
