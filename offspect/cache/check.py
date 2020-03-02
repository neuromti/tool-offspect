from typing import List, Dict, Union, Any
from pathlib import Path
from numpy import ndarray


Trace = ndarray  #: A trace, i.e. an array of samples for one or more channels stored in a cachefile


FileName = Union[str, Path]  #: The name of a file in the operating system

MetaValue = Union[
    str, int, float, List[str]
]  #: a specific  metadata attribute. Must be one of these types

MetaData = Dict[str, MetaValue]  #: A specific metadata element from an HDF5 cachefile

Annotations = Dict[
    str, Any
]  #: A dictionary with fields origin, origin attributes and trace attributes, the latter being a List of MetaData for each specific Trace

TraceAttributes = Dict[
    str, MetaValue
]  #:  Collapsed annotations with information on origin, origin attributes and a specific trace all in one Dictionary


IMPLEMENTED_READOUTS = ["contralateral_mep"]  #: currently implemented readout measures
VALID_SUFFIX = ".hdf5"  #: the  valid suffix for cachefiles


def check_consistency(annotations: List[Annotations]):
    """check whether a list of annotations is consistent
    
    For a list of attributes to be consistents, every origin file must be unique, and data may only come from a single subject. Additionally, channel_labels, samples pre/post, sampling must be identical for all traces"
    """
    o = [a["origin"] for a in annotations]
    if len(set(o)) != len(o):
        raise Exception(f"Origins are not unique {o}")

    keys_required_for_consistency = [
        "channel_labels",
        "samples_post_event",
        "samples_pre_event",
        "samplingrate",
        "subject",
        "readout",
    ]  # these keys must be identical across groups / origin files within a a cachefile
    for key in keys_required_for_consistency:
        check = [str(a["attrs"][key]) for a in annotations]
        if len(set(check)) != 1:
            raise Exception(f"{key} is inconsistent: {check}")


def check_valid_suffix(fname: FileName):
    "check whether the cachefile has a valid suffix"
    fname = Path(fname)
    if fname.suffix != VALID_SUFFIX:
        raise ValueError(f"{fname.suffix} has no valid suffix. Must be {VALID_SUFFIX}")
