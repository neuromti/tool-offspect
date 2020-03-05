"""
Smartmove
---------

These recordings come from the `smartmove robotic TMS <https://www.ant-neuro.com/products/smartmove>`_. This input format uses three files:

Data
****

EEG and EMG data is stored in the native file-format of the eego recording software. It can be loaded with `libeep <https://github.com/translationalneurosurgery/libeep>`_. During robotic TMS, the 64 EEG channels and the 8 EMG channels are stored in
separate :code:`.cnt` files.  

Coordinates
***********

The coordinates of the targets are stored in one or multiple :code:`targets_*.sav`-files in xml format. The filename of this save
file encodes experiment, subject pseudonym, date and hour, e.g.:
:code:`targets_<experiment>_<VvNn>_20190603_1624.sav`. These coordinates are the e.g. the grid of targets predefined before starting the mapping.

During the mapping procedure, the coordinates of the target positions, i.e. where the robot will be moved to, are saved in a :code:`documentation.txt`-file. Please note that these are the targets for the robotic movement, 
recorded, not the actual coordinates of stimulation. The actual coordinates at the time of stimulation do not appear to have been stored at all. 

Documentation of the syntax for these :code:`.txt` files will follow.

Module Content
**************

"""

from offspect.types import FileName, Coords
from pathlib import Path
from ast import literal_eval
from typing import List
from libeep import cnt_file


def load_documentation_txt(fname: FileName) -> Coords:
    "load a documentation.txt and return Coords"
    fname = Path(fname).expanduser().absolute()
    if not fname.name == "documentation.txt":
        raise ValueError(f"{fname} is not a valid documentation.txt")

    with fname.open("r") as f:
        lines = f.readlines()
    lines.append("\n")  # otherwise, last target is ignored
    coords = dict()
    target: List[str]
    target = []
    experiment = None
    subject = None
    idx = -1
    for line in lines:
        # a target block is complete
        if line == "\n":
            # make sure everything is from the same experiment and subject
            if subject is None:
                subject = target[-1]
            assert subject == target[-1]
            if experiment is None:
                experiment = target[-2]
            assert experiment == target[-2]

            # make sure the targets are consecutive and monoton
            if int(target[0]) != idx + 2:
                raise ValueError(f"{fname} is malformed")

            # parse the target data and add to the dictionary
            tmp = ", ".join(target[3].split(" "))
            xyz = literal_eval(f"[{tmp}]")
            target = []
            idx += 1
            coords[idx] = xyz[0:3]  # TODO unclear, discuss with Felix

        else:  # info not complete, we need to collect more lines
            target.append(line.strip())
    return coords


def load_cnt(fname: FileName):

    c = cnt_file(fname)

