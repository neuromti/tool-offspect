from pathlib import Path
from offspect.cache.file import CacheFile, populate
import argparse
import yaml
from typing import List
from liesl.files.xdf.inspect_xdf import peek
from offspect.cache.readout import get_valid_readouts

VALID_READOUTS: List[str] = get_valid_readouts(Path(__file__).stem)


def cli_pes(args: argparse.Namespace):
    print(args)

