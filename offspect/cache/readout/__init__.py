from typing import List
from pathlib import Path


ALL_READOUTS: List[str]  #: currently implemented readout measures
ALL_READOUTS = [f.stem for f in Path(__file__).parent.glob("*.py") if f.stem[0] != "_"]


def get_valid_readouts(prefix: str) -> List[str]:
    valid_readouts = []
    for readout in ALL_READOUTS:
        if readout.startswith(prefix):
            v = readout.split(".")[0].replace("_", "-").split(prefix)[1][1:]
            valid_readouts.append(v)
    return valid_readouts
