from typing import List
from pathlib import Path


VALID_READOUTS: List[str]  #: currently implemented readout measures
VALID_READOUTS = [
    f.stem for f in Path(__file__).parent.glob("*.py") if f.stem[0] != "_"
]
