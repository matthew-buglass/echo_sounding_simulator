import logging
import sys
from argparse import ArgumentParser

from utils.cli_parsing import parse_args

if __name__ == '__main__':
    # Get cli arguments
    print(parse_args(sys.argv[1:]))
