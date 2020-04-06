from os import environ
from typing import List, Generator
from offspect.types import FileName, Coordinate

if not environ.get("READTHEDOCS", False):
    from matprot.convert.coords import convert_xml_to_coords
    from matprot.convert.traces import (
        convert_mat,
        get_fs,
        get_onsets,
        get_enames,
    )
    from matprot.convert.traces import cut_into_traces as _cut_traces


def repeat_targets(coords: List[Coordinate], repeat: int = 5) -> Generator:
    coordinator = iter(coords)
    while True:
        try:
            target = next(coordinator)
            for i in range(0, repeat):
                yield target
        except StopIteration:
            return


def get_coords_from_xml(xmlfile: FileName, repeat: int = 5) -> List[Coordinate]:
    targets = convert_xml_to_coords(xmlfile)
    coords = list(repeat_targets(targets, repeat))
    return coords
