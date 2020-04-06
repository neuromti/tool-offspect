from typing import Any, Dict, List
import yaml
from pathlib import Path
import datetime
from offspect.cache.readout import get_valid_readouts
from offspect.types import Annotations, MetaData
from offspect.cache.readout import valid_origin_keys, valid_trace_keys
from offspect import release
import importlib
from functools import lru_cache
from math import nan, inf


def decode(value: str) -> Any:
    "decode any value from string"
    dec = yaml.load(value, Loader=yaml.Loader)
    if type(dec) == list:
        _d = []
        for i in dec:
            if type(i) == str:
                _d.append(decode(i))
            else:
                _d.append(dec)
        dec = _d
    if dec == "nan":
        dec = nan
    if dec == "inf":
        dec = inf
    return dec


def encode(value: Any) -> str:
    "encode any value to string for storing as TraceAttribute value"
    if type(value) == type(Path()):
        value = str(value)
    if type(value) == datetime.datetime:
        value = str(value)
    if type(value) == str:
        return value
    if type(value) == list:
        return str(value)

    enc = yaml.dump(value, Dumper=yaml.Dumper).splitlines()[0]
    if "!!" in enc:
        raise ValueError(
            "Please use only literals, and if necessary cast with float, str or int"
        )

    return enc


@lru_cache(maxsize=1)
def get_valid_trace_keys(rio: str) -> List[str]:
    ri, ro = rio.split("_")
    try:
        m = importlib.import_module(f"offspect.input.{ri}.{ro}")
        return m.valid_keys + valid_trace_keys  # type: ignore
    except Exception:
        raise ImportError(
            f"offspect.input.{ri}.{ro} is invalid. Please define valid_keys in its __init__.py"
        )


class AnnotationFactory:
    """A factory to create new annotations
    
    args
    ----
    readin: str
        the format of the data being readin, e.g. tms or pes
    readout: str
        the format of how the data will be used for display and analysis, e.g. wave, cmep, imep, erp
    origin:str
        the original source-file from where this data is coming from

    
    """

    def _clear_annotations(self):
        self.anno: Annotations = dict()
        self.anno["origin"] = ""
        self.anno["attrs"]: MetaData = dict()
        for key in valid_origin_keys:
            self.anno["attrs"][key] = ""
        self.anno["traces"]: List[MetaData] = []
        self.set("version", release)

    def __init__(self, readin: str, readout: str, origin=""):
        valid_readouts = get_valid_readouts(readin)
        if readout not in valid_readouts:
            raise NotImplementedError(
                f"{readout} invalid, only {valid_readouts} are allowed"
            )
        self._clear_annotations()
        self.set("origin", origin)
        self.set("readout", readout)
        self.set("readin", readin)

    def set(self, key: str, value: Any):
        "perform checks for validity and sets a value for a global field"
        if key == "origin":
            self.anno["origin"] = encode(value)
        else:
            if key not in valid_origin_keys:
                raise KeyError(
                    f"{key} is invalid, only {valid_origin_keys} are allowed"
                )
            else:
                self.anno["attrs"][key] = encode(value)

    def get(self, key: str):
        "returns a value for a global field"
        if key == "origin":
            return decode(self.anno["origin"])
        else:
            if key not in valid_origin_keys:
                raise KeyError(
                    f"{key} is invalid, only {valid_origin_keys} are allowed"
                )
            else:
                return decode(self.anno["attrs"][key])

    @property
    def rio(self):
        """The readin/out parameter
        
        This parameter defines which keys are valid for the TraceAttributes and defines what the GUI should show
        """
        ri = self.anno["attrs"]["readin"]
        ro = self.anno["attrs"]["readout"]
        return ri + "_" + ro

    def __str__(self):
        return str(self.anno)

    def __repr__(self):
        ri = self.anno["attrs"]["readin"]
        ro = self.anno["attrs"]["readout"]
        o = self.anno["origin"]
        return f"AnnotationFactory('{ri}','{ro}','{o}')"

    @property
    def valid_trace_keys(self):
        "a list of which keys are required and valid for the TraceAttributes"
        return get_valid_trace_keys(self.rio)

    def append_trace_attr(self, attrs: MetaData):
        "append a TraceAttribute to the current list of TraceAttributes"
        tattrs = dict()
        for key in self.valid_trace_keys:
            if key in attrs.keys():
                e = encode(attrs[key])

                tattrs[key] = e
            else:
                # print(f"Defaulting to '' for {key}")
                tattrs[key] = ""
        self.anno["traces"].append(tattrs)
