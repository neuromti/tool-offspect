from pathlib import Path
from typing import Union
from ..cache.file import CacheFile
import argparse


def cli_peek(args: argparse.Namespace):
    print(CacheFile(args.fname))


def main():
    parser = argparse.ArgumentParser(
        prog="offspect",
        description="Create, manipulate and inspect cachefiles for offline inspection of evoked potentials",
    )
    subparsers = parser.add_subparsers(dest="sub")

    # PEEK --------------------------------------------------------------------
    peek = subparsers.add_parser(
        name="peek", help="peek into a cachefile and print essential information"
    )
    peek.add_argument("fname", help="filename to peek into", type=str)

    # eventually, parse -------------------------------------------------------
    args, _ = parser.parse_known_args()
    if args.sub == "peek":
        cli_peek(args)
    else:
        print("No valid subcommand specified")

