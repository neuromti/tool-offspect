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


VALID_READOUTS = ["contralateral_mep"]  #: currently implemented readout measures
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


isint = lambda x: isinstance(x, int)
isfloat = lambda x: isinstance(x, float)
isnumeric = lambda x: (isint(x) or isfloat(x))
isstr = lambda x: isinstance(x, str)
islist = lambda x: isinstance(x, list)
iscoords = lambda x: islist(x) and len(x) == 3 and all((isnumeric(x) for x in x))
isTsince = lambda x: (isnumeric(x) and x > 0) or x == None or x == ""
isbool = lambda x: isinstance(x, bool)

GENERIC_TRACEKEYS = {
    "id": isint,
    "event_name": isstr,
    "event_sample": isint,
    "event_time": isfloat,
    "xyz_coords": iscoords,
    "onset_shift": isint,
    "reject": isbool,
    "comment": isstr,
    "examiner": isstr,
}

TRACEKEYS = dict()
TRACEKEYS["contralateral_mep"] = {
    "time_since_last_pulse_in_s": isTsince,
    "stimulation_intensity_mso": isnumeric,
    "stimulation_intensity_didt": isnumeric,
    "neg_peak_magnitude_uv": isnumeric,
    "neg_peak_latency_ms": isnumeric,
    "pos_peak_magnitude_uv": isnumeric,
    "pos_peak_latency_ms": isnumeric,
    "zcr_latency_ms": isnumeric,
}


def check_trace_attributes(readout: str, attributes: TraceAttributes):
    """check whether all attributes of a trace are correctly formatted 
    according to readout"""
    if readout not in VALID_READOUTS:
        raise NotImplementedError(f"{readout} is not implemented")

    TKEYS = GENERIC_TRACEKEYS.copy()
    TKEYS.update(**TRACEKEYS[readout])
    for key, foo in TKEYS.items():
        try:
            if not foo(attributes[key]):
                raise ValueError(f"{attributes[key]} has invalid type")
        except KeyError:
            raise KeyError(f"{key} not in the attributes keys")
        except Exception as e:
            raise e

