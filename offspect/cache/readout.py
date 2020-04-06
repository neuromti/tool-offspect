"""
Generic MetaData fields implemented in all readouts
---------------------------------------------------

"""

from typing import List
from pathlib import Path


def get_all_rios():
    "get all currently implemented readin/readout pairs"
    READOUTS: List[str] = []  #: all currently implemented readouts
    READINS: List[str] = []  #: all currently implemented readins
    RIOS: List[str] = []  #: all currently available readin/readout combos
    for ri in (Path(__file__).parent.parent / "input").iterdir():
        if ri.is_dir() and not ri.name.startswith("_"):
            READINS.append(ri.stem)
            for ro in ri.iterdir():
                if ro.is_dir() and not ro.name.startswith("_"):
                    READOUTS.append(ro.stem)
                    rio = f"{ri.stem}-{ro.stem}"
                    RIOS.append(rio)
    return RIOS


ALL_RIOS = get_all_rios()  #: all currently available readin/readout combos


def get_valid_readouts(readin: str) -> List[str]:
    "return a list of valid readouts for a given readin"
    valid_readouts = []
    for readout in ALL_RIOS:
        if readout.startswith(readin):
            v = readout.split(".")[0].replace("_", "-").split(readin)[1][1:]
            valid_readouts.append(v)
    return valid_readouts


must_be_identical_in_merged_file = [
    "channel_labels",
    "channel_of_interest",
    "samples_post_event",
    "samples_pre_event",
    "samplingrate",
    "subject",
    "readout",
    "readin",
    "version",
]  #: must be identical across original files merged into this cachefile

can_vary_across_merged_files = [
    "global_comment",
    "filedate",
]  #: information about the origin file

valid_origin_keys = must_be_identical_in_merged_file + can_vary_across_merged_files

valid_trace_keys = [
    "id",
    "event_name",
    "event_sample",
    "event_time",
    "onset_shift",
    "time_since_last_pulse_in_s",
    "reject",
    "comment",
    "examiner",
]  #: information contained in every trace, regardless of readout
