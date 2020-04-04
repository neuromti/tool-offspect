from typing import Any, Dict, List
import yaml
from pathlib import Path
import datetime
from offspect.cache.readout import get_valid_readouts
from offspect.types import Annotations, MetaData
from offspect.cache.readout.generic import valid_origin_keys, valid_trace_keys
from offspect import release
import importlib
from functools import lru_cache


def decode(value: str) -> Any:
    "decode any value from string"
    return yaml.load(value, Loader=yaml.Loader)


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
    return yaml.dump(value, Dumper=yaml.Dumper).splitlines()[0]


class AnnotationFactory:
    def clear_annotations(self):
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
        self.clear_annotations()
        self.set("origin", origin)
        self.set("readout", readout)
        self.set("readin", readin)

    def set(self, key: str, value: Any):
        if key == "origin":
            self.anno["origin"] = encode(value)
        else:
            if key not in valid_origin_keys:
                raise KeyError(
                    f"{key} is invalid, only {valid_origin_keys} are allowed"
                )
            else:
                self.anno["attrs"][key] = encode(value)

    def get(self, key: str, value: Any):
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
        
        limits the valid TraceAttributes and defines what the GUI should show        
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
    @lru_cache(maxsize=1)
    def valid_trace_keys(self):
        "a list of which keys are required and valid for the TraceAttributes"
        m = importlib.import_module(f"offspect.cache.readout.{self.rio}")
        return m.valid_keys + valid_trace_keys

    def append_trace_attrs(self, attrs: MetaData):
        "append a TraceAttribute to the current list of TraceAttributes"
        tattrs = dict()
        for key in self.valid_trace_keys:
            if key in attrs.keys():
                e = encode(attrs[key])
                if "!!" in e:
                    raise ValueError(
                        "Please use only safe values, if necessary cast with float, str or int first!"
                    )
                tattrs[key] = e
            else:
                print(f"Defaulting to '' for {key}")
                tattrs[key] = ""
        self.anno["traces"].append(tattrs)
