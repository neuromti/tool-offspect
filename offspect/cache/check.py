from typing import List, Dict, Union, Any, Callable
from pathlib import Path
from numpy import ndarray
import yaml
import re
import datetime
from offspect.types import *
from math import inf, isnan

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


def isint(x):
    return isinstance(x, int)


def isfloat(x) -> bool:
    if x is None or x == "":
        return False
    return isinstance(x, float) or isnan(x)


def isnumeric(x) -> bool:
    return isint(x) or isfloat(x)


def isstr(x) -> bool:
    return isinstance(x, str)


def islist(x) -> bool:
    return isinstance(x, list)


def iscoords(x) -> bool:
    if not (islist(x) and len(x) == 3 and all((isnumeric(x) for x in x))):
        print(f"{x} is {type(x)}")
        return False
    else:
        return True


def isindex(x: str) -> bool:
    if x is None or x == "" or type(x) is not str:
        return False
    try:
        ix = int(x)
        if ix < 0:
            return False
    except ValueError:
        return False
    return (ix - float(x)) < 0.000001


def isTsince(x) -> bool:
    return (isnumeric(x) and x > 0) or x == inf or x is None


def isbool(x) -> bool:
    return isinstance(x, bool)


def ischanlist(x) -> bool:
    return islist(x) and all(isstr(c) for c in x)


def isversion(x) -> bool:
    r = re.compile("[0-9]+[.][0-9]+[.][0-9]+[a-zA-Z]{0,1}")
    try:
        return r.fullmatch(x) != None
    except:
        return False


def isfiledate(x) -> bool:
    d = yaml.load(f"filedate: {x}", Loader=yaml.Loader)["filedate"]
    return type(d) == datetime.datetime or type(d) == datetime.date


ORIGINKEYS = {
    "channel_labels": ischanlist,
    "samples_post_event": isint,
    "samples_pre_event": isint,
    "samplingrate": isint,
    "subject": isstr,
    "readout": isstr,
    "comment": isstr,
    "filedate": isfiledate,
    "history": isstr,
    "version": isversion,
}  #: A dictionary specifying the keys and required types which all origin attributes  must implement, independent of the readout used

GENERIC_TRACEKEYS = {
    "id": isint,
    "event_name": isstr,
    "event_sample": isint,
    "event_time": isfloat,
    "xyz_coords": iscoords,
    "onset_shift": isint,
    "time_since_last_pulse_in_s": isTsince,
    "reject": isbool,
    "comment": isstr,
    "examiner": isstr,
}  #: A dictionary specifying the keys and required types which all TraceAttributes  must implement, independent of the readout used

SPECIFIC_TRACEKEYS = (
    dict()
)  #: A dictionary containing for all mmplemented readouts their specific  keys for the TraceAttributes and as values a functions checking the validity of the respective TraceAttributes value
CONTRALATERAL_MEP_KEYS = {
    "stimulation_intensity_mso": isnumeric,
    "stimulation_intensity_didt": isnumeric,
    "neg_peak_magnitude_uv": isnumeric,
    "neg_peak_latency_ms": isnumeric,
    "pos_peak_magnitude_uv": isnumeric,
    "pos_peak_latency_ms": isnumeric,
    "zcr_latency_ms": isnumeric,
}  #: A dictionary specifying the keys and required types if the readout is "contralateral_mep"

SPECIFIC_TRACEKEYS["contralateral_mep"] = CONTRALATERAL_MEP_KEYS


def check_metadata(readout: str, attributes: TraceAttributes):
    """check whether all attributes of a trace are correctly formatted 
    according to readout see :data:`~.offspect.cache.check.GENERIC_TRACEKEYS` and :data:`~.SPECIFIC_TRACEKEYS`
    
    """
    if readout not in VALID_READOUTS:
        raise NotImplementedError(f"{readout} is not implemented")

    TKEYS = GENERIC_TRACEKEYS.copy()
    TKEYS.update(**SPECIFIC_TRACEKEYS[readout])
    TKEYS.update(**ORIGINKEYS)
    for key, foo in TKEYS.items():
        try:
            if not foo(attributes[key]):
                raise ValueError(f"{key}:{attributes[key]} has invalid type")
        except KeyError:
            raise KeyError(f"{key} not in the attributes keys")
        except Exception as e:
            raise e


def filter_trace_attrs(attrs: TraceAttributes) -> TraceAttributes:
    """"discard all fields from TraceAttributes that are not valid for its readout
    
    args
    ----
    attrs: TraceAttributes
        the raw TraceAttributes with possibly superfluous or invalid fields

    returns
    -------
    filtered: TraceAttributes
        the filtered TraceAttributes


    .. note::
        will raise an Exception if the type of the fields are not in correspondence with the :data:`GENERIC_TRACEKEYS` and the :data:`SPECIFIC_TRACEKEYS` for the attributes readout

    """
    readout = str(attrs["readout"])
    if readout not in VALID_READOUTS:
        raise NotImplementedError(f"{readout} is not implemented")
    TKEYS = GENERIC_TRACEKEYS.copy()
    TKEYS.update(**SPECIFIC_TRACEKEYS[readout])
    # check_metadata(readout, attrs)
    filtered = attrs.copy()
    for key in attrs.keys():
        if key not in TKEYS.keys():
            filtered.pop(key)
    return filtered

