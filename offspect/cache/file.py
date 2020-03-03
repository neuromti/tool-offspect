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
    check_metadata,
    FileName,
    MetaValue,
    MetaData,
    Annotations,
    TraceData,
    TraceAttributes,
    filter_traceattrs,
)
from functools import lru_cache

read_file = partial(
    h5py.File, mode="r", libver="latest", swmr=True
)  #: open an hdf5 file in single-write-multiple-reader mode


write_file = partial(
    h5py.File, mode="r+", libver="latest", swmr=True
)  #: open an hdf5 file in single-write-multiple-reader mode


class CacheFile:
    """instantiate a new cachefile from HDD
    
    args
    ----
    fname: FileName
        path to the file      
          
    """

    def __init__(self, fname: FileName):
        self.fname = Path(fname).expanduser().absolute()
        if self.fname.exists() == False:
            raise FileNotFoundError(f"{self.fname} does not exist")
        check_valid_suffix(fname)

    def get_trace_data(self, idx: int) -> TraceData:
        """return TraceData for a specific traces in the file
        
        """
        return read_trace(self, idx=idx, what="data")

    def get_trace_attrs(self, idx: int) -> TraceAttributes:
        """return TraceAttributes for a specific traces in the file
        
        """
        return read_trace(self, idx=idx, what="attrs")

    def set_trace_attrs(self, attrs: TraceAttributes):
        if not self.fname == attrs["original_file"]:
            raise ValueError("These attributes did not originate from this CachFile")
        update_trace_attributes(attrs)

    @property
    def origins(self) -> List[str]:
        "returns a list of original files used in creating this cachefile"
        with read_file(self.fname) as f:
            origins = list(f.keys())
        return origins

    @property
    def annotations(self) -> List[Annotations]:
        """returns a list of annotations within this cachefile
        
        """
        return recover_annotations(self)

    @property
    def attrs(self) -> Dict[str, MetaData]:
        "return a dictionary of metadata for each origin"
        a = recover_annotations(self)
        d = dict()
        for key, anno in zip(self.origins, a):
            d[key] = anno["attrs"]
        return d

    @property
    def traces(self) -> List[Tuple[TraceAttributes, TraceData]]:
        """return a list of paired TraceAttributes and TraceData for all traces in the file
        
        Example::

            for (attrs, data) in c.traces: 
                pass
            print(attrs)
        """
        return list(yield_traces(self))

    def __str__(self) -> str:
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

    @lru_cache(maxsize=1)
    def __len__(self) -> int:
        cnt = 0
        with read_file(self.fname) as f:
            for origin in f.keys():
                for idx, _ in enumerate(f[origin]["traces"], start=cnt + 1):
                    pass
                cnt = idx
        return int(cnt)


def yield_trdata(cf: CacheFile) -> Iterator:
    with read_file(cf.fname) as f:
        for origin in f.keys():
            for idx in f[origin]["traces"]:
                # load data fresh from file
                f[origin]["traces"][idx].id.refresh()
                yield parse_tracedata(f[origin]["traces"][idx])


def yield_trattrs(cf: CacheFile) -> Iterator[TraceAttributes]:
    with read_file(cf.fname) as f:
        for origin in f.keys():
            for idx in f[origin]["traces"]:
                yml = dict()
                yml["origin"] = origin
                yml["attrs"] = parse_traceattrs(f[origin].attrs)
                dset = f[origin]["traces"][idx]
                dset.id.refresh()  # load fresh from file
                yml["trace"] = parse_traceattrs(dset.attrs)
                check_metadata(yml["attrs"]["readout"], yml["trace"])
                yield yml


def yield_traces(cf: CacheFile) -> Iterator[TraceData]:
    attrs = yield_trattrs(cf)
    traces = yield_trdata(cf)
    while True:
        try:
            a = next(attrs)
            t = next(traces)
            yield (a, t)
        except StopIteration:
            return


def update_trace_attributes(attrs: TraceAttributes):
    index = attrs["original_index"]
    fname = attrs["original_file"]
    attrs = filter_traceattrs(attrs)
    if type(index) != int:
        raise ValueError("Index must be an integer")
    if index >= 0:
        cnt = -1
        with write_file(fname) as f:
            for origin in f.keys():
                for idx, key in enumerate(f[origin]["traces"], start=cnt + 1):
                    if idx == index:
                        dset = f[origin]["traces"][key]
                        for key in attrs.keys():
                            dset.attrs[str(key)] = str(attrs[key])
                        return
                    cnt = idx

    raise IndexError(f"{index} not in cachefile")


def read_trace(
    cf: CacheFile, idx: int, what: str = "attrs"
) -> Union[TraceData, TraceAttributes]:
    """read either metadata or attributes for a specific trace
    
    args
    ----
    cf: CacheFile
        for which file
    idx: int
        which trace to load
    what: str 
        whether to load 'data' or 'attrs'. defaults to attrs
    
    """
    if type(idx) != int:
        raise ValueError("Index must be an integer")
    if idx >= 0:
        cnt = -1
        with read_file(cf.fname) as f:
            for origin in f.keys():
                for ix, key in enumerate(f[origin]["traces"], start=cnt + 1):
                    if idx == ix:
                        dset = f[origin]["traces"][key]
                        dset.id.refresh()  # load fresh from file
                        if what == "attrs":
                            attrs = parse_traceattrs(dset.attrs)
                            attrs["original_file"] = cf.fname
                            attrs["original_index"] = idx
                            check_metadata(attrs["readout"], attrs)
                            return attrs
                        elif what == "data":
                            data = parse_tracedata(dset)
                            return data
                        else:
                            raise NotImplementedError(f"{what} can not be loaded")
                    cnt = idx

    raise IndexError(f"{idx} not in cachefile")


def parse_traceattrs(attrs: h5py.AttributeManager) -> MetaData:
    """parse any metadata from a cachefile and return it as Dict    
    """
    d = dict(attrs)
    for key, val in d.items():
        try:
            d[key] = ast.literal_eval(val)
        except (SyntaxError, ValueError):  # for subject and filedate
            pass
    return d


def parse_tracedata(dset: h5py.Dataset) -> TraceData:
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
            yml["attrs"] = parse_traceattrs(f[origin].attrs)
            readout = yml["attrs"]["readout"]
            trace_attrs = []
            for idx in f[origin]["traces"]:
                dset = f[origin]["traces"][idx]
                dset.id.refresh()  # load fresh from file
                tattr = parse_traceattrs(dset.attrs)
                check_metadata(readout, tattr)
                trace_attrs.append(tattr)
            yml["traces"] = trace_attrs
            events.append(yml)
    return events


def recover_parts(cf: CacheFile) -> Tuple[List[Annotations], List[List[TraceData]]]:
    """recover the two parts of a cachefile, i.e. annotations and traces
    
    args
    ----
    cf: CacheFile
        the cachefile from which to recover

    returns
    -------
    annotations: List[Annotations]
        a list of annotations, i.e the metadata of all sourcefiles in the cachefile organized as [sourcesfiles][Annotations]
    traces: List[List[TraceData]]
        a list of the traces of all sourcefiles saved in the cachefile 
        organized as [sourcefiles][traceidx][TraceData]

    """
    with read_file(cf.fname) as f:
        events, traces = [], []
        for origin in f.keys():
            yml = dict()
            yml["origin"] = origin
            yml["attrs"] = parse_traceattrs(f[origin].attrs)

            trace_attrs = []
            trace_data = []
            for idx in f[origin]["traces"]:
                dset = f[origin]["traces"][idx]
                dset.id.refresh()  # load fresh from file
                trace_attrs.append(parse_traceattrs(dset.attrs))
                trace_data.append(parse_tracedata(dset))
            yml["traces"] = trace_attrs
        events.append(yml)
        traces.append(trace_data)
    return events, traces


def populate(
    tf: FileName, annotations: List[Annotations], traceslist: List[List[TraceData]]
) -> FileName:
    """create a new cachefile from a annotations and traces
    
    args
    ----
    tf: FileName
        the name of the file to be created. will overwrite an existing file
    annotations: List[Attributes]
        a list of annotation dictionaries
    traceslist: List[List[TraceData]]
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

