from typing import List, Dict, Union, Any, Callable
from pathlib import Path
from numpy import ndarray
import yaml
import re
import datetime
from offspect.types import *
from math import inf, isnan
from offspect.cache.attrs import get_valid_trace_keys
from offspect.cache.readout.generic import must_be_identical_in_merged_file

VALID_SUFFIX = ".hdf5"  #: the  valid suffix for cachefiles


def check_consistency(annotations: List[Annotations]):
    """check whether a list of annotations is consistent
    
    For a list of attributes to be consistents, every origin file must be unique, and data may only come from a single subject. Additionally, channel_labels, samples pre/post, sampling must be identical for all traces"
    """
    o = [a["origin"] for a in annotations]
    ro = set([a["attrs"]["readout"] for a in annotations])
    ri = set([a["attrs"]["readin"] for a in annotations])

    if len(set(o)) != len(o):
        raise Exception(f"Origins are not unique {o}")
    if len(ro) != 1:
        raise Exception(f"Readouts are not identical: {ro}")
    if len(ri) != 1:
        raise Exception(f"Readins are not identical: {ri}")

    rio = ri.pop() + "_" + ro.pop()
    keys_required_for_consistency = get_valid_trace_keys(rio)

    # these keys must be identical across groups / origin files within a a cachefile
    for key in must_be_identical_in_merged_file:
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
    if x == "":
        return True
    d = yaml.load(f"filedate: {x}", Loader=yaml.Loader)["filedate"]
    return type(d) == datetime.datetime or type(d) == datetime.date
