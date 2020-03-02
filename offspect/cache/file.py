from typing import Union, List, Dict, Tuple, Iterator
from pathlib import Path
import h5py
import yaml
import numpy as np
from numpy import ndarray
from functools import partial
import ast
from .check import (
    check_consistency,
    check_valid_suffix,
    FileName,
    MetaValue,
    MetaData,
    Annotations,
    Trace,
    TraceAttributes,
)


read_file = partial(
    h5py.File, mode="r", libver="latest", swmr=True
)  #: open an hdf5 file in single-write-multiple-reader mode


class CacheFile:
    """instantiate a new cachefile from HDD
    
    args
    ----
    fname: FileName
        path to the file      
          
    """

    def __init__(self, fname: FileName):
        self.fname = Path(fname).absolute().expanduser()
        if self.fname.exists() == False:
            raise FileNotFoundError(f"{self.fname} does not exist")
        check_valid_suffix(fname)

    @property
    def origins(self) -> List[str]:
        "returns a list of original files used in creating this cachefile"
        with read_file(self.fname) as f:
            origins = list(f.keys())
        return origins

    @property
    def annotations(self) -> List[Annotations]:
        "returns a list of annotations within this cachefile"
        return recover_annotations(self)

    @property
    def traces(self) -> List[Tuple[TraceAttributes, Trace]]:
        "return attributes and data for all traces in the file in consecutive fashion"
        return list(yield_traces(self))

    def __str__(self) -> str:
        self.traces
        s = ""
        h = "-" * 79 + "\n"
        gap = 20
        for attrs in recover_annotations(self):
            k = "origin"
            v = attrs[k]
            o = f"{k:{gap}s} : {v}\n"

            a = ""
            for k, v in attrs["attrs"].items():
                a += f"{k:{gap}s} : {v}\n"

            v = len(attrs["traces"])
            k = "traces_count"
            tc = f"{k:{gap}s} : {v}\n"

            s += "".join((h, o, a, tc))
        return s


def yield_trdata(cf: CacheFile) -> Iterator:
    with read_file(cf.fname) as f:
        for origin in f.keys():
            for idx in f[origin]["traces"]:
                # load data fresh from file
                f[origin]["traces"][idx].id.refresh()
                yield parse_trace(f[origin]["traces"][idx])


def yield_trattrs(cf: CacheFile) -> Iterator[TraceAttributes]:
    with read_file(cf.fname) as f:
        for origin in f.keys():
            for idx in f[origin]["traces"]:
                yml = dict()
                yml["origin"] = origin
                yml["attrs"] = parse_attrs(f[origin].attrs)
                dset = f[origin]["traces"][idx]
                dset.id.refresh()  # load fresh from file
                yml["trace"] = parse_attrs(dset.attrs)
                yield yml


def yield_traces(cf: CacheFile) -> Iterator[Trace]:
    attrs = yield_trattrs(cf)
    traces = yield_trdata(cf)
    while True:
        try:
            a = next(attrs)
            t = next(traces)
            yield (a, t)
        except StopIteration:
            return


def parse_attrs(attrs: h5py.AttributeManager) -> MetaData:
    "parse any metadata from a cachefile and return it as Dict"
    d = dict(attrs)
    for key, val in d.items():
        try:
            d[key] = ast.literal_eval(val)
        except (SyntaxError, ValueError):  # for subject and filedate
            pass
    return d


def parse_trace(dset: h5py.Dataset) -> Trace:
    "parse a hdf5 dataset from a cachefile and return it as a trace"
    return np.asanyarray(dset, dtype=float)


def recover_annotations(cf: CacheFile) -> List[Annotations]:
    """"recover the file and annotations from a cachefile

    args
    ----
    cf: CacheFile
        the cachefile from which to recover

    returns
    -------
    annotations: List[Annotations]
        a list of annotations, where annotations are the collapsed metadata of all sourcefiles in the cachefile organized as [sourcesfiles][Annotations] :class:`~.offspect.cache.file.Annotations`
    """

    with read_file(cf.fname) as f:
        events = []
        for origin in f.keys():
            yml = dict()
            yml["origin"] = origin
            yml["attrs"] = parse_attrs(f[origin].attrs)

            trace_attrs = []
            for idx in f[origin]["traces"]:
                dset = f[origin]["traces"][idx]
                dset.id.refresh()  # load fresh from file
                trace_attrs.append(parse_attrs(dset.attrs))
            yml["traces"] = trace_attrs
            events.append(yml)
    return events


def recover_parts(cf: CacheFile) -> Tuple[List[Annotations], List[List[Trace]]]:
    """recover the two parts of a cachefile, i.e. annotations and traces
    
    args
    ----
    cf: CacheFile
        the cachefile from which to recover

    returns
    -------
    annotations: List[Annotations]
        a list of annotations, i.e the metadata of all sourcefiles in the cachefile organized as [sourcesfiles][Annotations]
    traces: List[List[Trace]]
        a list of the traces of all sourcefiles saved in the cachefile 
        organized as [sourcefiles][traceidx][Trace]

    """
    with read_file(cf.fname) as f:
        events, traces = [], []
        for origin in f.keys():
            yml = dict()
            yml["origin"] = origin
            yml["attrs"] = parse_attrs(f[origin].attrs)

            trace_attrs = []
            trace_data = []
            for idx in f[origin]["traces"]:
                dset = f[origin]["traces"][idx]
                dset.id.refresh()  # load fresh from file
                trace_attrs.append(parse_attrs(dset.attrs))
                trace_data.append(parse_trace(dset))
            yml["traces"] = trace_attrs
        events.append(yml)
        traces.append(trace_data)
    return events, traces


def populate(
    tf: FileName, annotations: List[Annotations], traceslist: List[List[Trace]]
) -> FileName:
    """create a new cachefile from a annotations and traces
    
    args
    ----
    tf: FileName
        the name of the file to be created. will overwrite an existing file
    annotations: List[Attributes]
        a list of annotation dictionaries
    traceslist: List[List[Traces]]
        a list of list of traces
    
    returns
    -------
    fname: FileName
        the path to the freshly populated cachefile
    
    """
    tf = Path(tf).expanduser().absolute()
    # populate the cachefile
    with h5py.File(tf, "w") as f:
        print(f"Merging into {tf.name} from:")
        for settings, traces in zip(annotations, traceslist):
            print("   -", settings["origin"])

            ofile = f.create_group(settings["origin"])
            # fill with ofile-attributes
            attrs = settings["attrs"]
            for key, val in attrs.items():
                ofile.attrs.modify(str(key), str(val))

            # fill with trace-data and trace-attributes
            tracegrp = ofile.create_group("traces")

            for tattr, trace in zip(settings["traces"], traces):
                tattr.update(**attrs)
                idx = str(tattr["id"])
                trace = tracegrp.create_dataset(idx, data=trace)
                for k, v in tattr.items():
                    trace.attrs.modify(str(k), str(v))
    return tf


def merge(to: FileName, sources: List[FileName]) -> FileName:
    """merge one or more cachefiles into one file

    args
    ----
    to: FileName
        the name of the file to be written into. Will be overwritten, if already existing
    sources: List[FileName]
        a list of source files from which we will read traces and annotations

    returns
    -------
    fname: FileName
        the name of the target file
    """
    sources = [Path(source).expanduser().absolute() for source in sources]
    to = Path(to).expanduser().absolute()
    check_valid_suffix(to)
    if to.exists():
        print(f"MERGE:WARNING: {to.name} already exists and will be overwritten")
        to.unlink()

    a: List[Dict] = []
    t: List[ndarray] = []
    for source in sources:
        attrs, traces = recover_parts(CacheFile(source))
        a.extend(attrs)
        t.extend(traces)

    check_consistency(a)
    fname = populate(tf=to, annotations=a, traceslist=t)
    return fname

