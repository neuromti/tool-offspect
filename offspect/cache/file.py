"""
CacheFile
---------
The python interface to the :py:class:`~.CacheFile` which checks for filename
validity during instantiation. When one of its properties are called, it loads
and parses the metadata and datasets fresh from the hdf5 and aggregatates them.
Example::

   from offspect.api import CacheFile
   cf = CacheFile("example.hdf5")
   print(cf)

"""
from typing import Union, List, Dict, Tuple, Iterator
from pathlib import Path
import h5py
import yaml
import numpy as np
from numpy import ndarray
from functools import partial
import ast
from functools import lru_cache
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
    filter_trace_attrs,
    isindex,
)
from math import inf, nan

read_file = partial(
    h5py.File, mode="r", libver="latest", swmr=True
)  #: open an hdf5 file in single-write-multiple-reader mode


write_file = partial(
    h5py.File, mode="r+", libver="latest", swmr=True
)  #: open an hdf5 file in single-write-multiple-reader mode

# -----------------------------------------------------------------------------
class CacheFile:
    """instantiate a new cachefile from HDD
    
    args
    ----
    fname: FileName
        path to the file      
          
    For each readout, a specific set of fields must be in the metadata of a trace. Whenever attributes are read or written, the validity of the metadata will automatically be checked to be consistent with its 'readout'.
    """

    def __init__(self, fname: FileName):
        self.fname = Path(fname).expanduser().absolute()
        if self.fname.exists() == False:
            raise FileNotFoundError(f"{self.fname} does not exist")
        check_valid_suffix(fname)

    def get_trace_data(self, idx: int) -> TraceData:
        """return TraceData for a specific traces in the file
                
        args
        ----
        idx: int
            which trace to pick.
        returns
        -------
        attrs: TraceData 
            the date stored for this trace.
        
        .. note::
           This is a read-only attribute, and raw data can never be overwritten with the CacheFile interface. If you need to perform
           any preprocessing steps, manage the TraceData with a low-level interface, e.g. :func:`~.populate`.
        """
        return read_trace(self, idx=idx, what="data")

    def get_trace_attrs(self, idx: int) -> TraceAttributes:
        """read the TraceAttributes for a specific traces in the file
        
        args
        ----
        idx: int
            which trace to pick.
        returns
        -------
        attrs: TraceAttributes 
            the collapsed attributes for this trace.
        
    
        Example::
        
            cf = CacheFile("example.hdf5")
            for i in len(cf):
                attrs = cf.get_trace_attrs(i)


        .. note::

           The TraceAttributes contain the metadata of this trace, and  the metadata of its parent group, i.e. sourcefile. Additionally, two fields will be added, containing information about the 'cache_file' and the 'cache_file_index'. The number of fields is therefore larger than the number of fields valid for TraceAttributes according to :func:`~.filter_trace_attrs`. This is no problem, because when you update with :meth:`~.set_trace_attrs`, these fields will be used for safety checks and subsequently discarded.

        """
        return read_trace(self, idx=idx, what="attrs")

    def set_trace_attrs(self, idx: int, attrs: TraceAttributes):
        """update the attributes of a specific trace
        
        args
        ----
        idx: int
            at which index to overwrite
        attrs: TraceAttributes
            with which attributes to overwrite
        

        Example::

            import datetime
            now = str(datetime.datetime.now())
            cf = CacheFile("example.hdf5")
            attrs = cf.get_trace_attrs(0)
            attrs["comment"] = now
            cf.set_trace_attrs(0, attrs)

        .. note::

           Because we expect the TraceAttributes to originate from a CacheFiles
           :meth:`~.get_trace_attrs` method, we expect them to have information
           about their original file and index included. For safety reasons,
           you have to specify the index when calling this setter. Additionally, the original file must be this instance of CacheFile.
           If you want to directly overwrite an arbitrary attribute without
           this safety checks, update the values for original_file and original_index and use :func:`~.update_trace_attributes`. 
           Additionally, please note that while :meth:`~.get_trace_attrs`
           returns a complete dictionary of attributes, including thise that apply to the whole group or origin file, only valid fields for 
           trace metadata will be saved, i.e. those fields which are in correspondence with the "readout" parameter (see :func:`~.filter_trace_attrs`).

        """
        if not "cache_file" in attrs.keys() or not "cache_file_index" in attrs.keys():
            raise ValueError(
                "This attributes do not originate from a CacheFile. Information about its origin is missing"
            )

        if not str(self.fname) == attrs["cache_file"]:
            raise ValueError("These attributes did not originate from this CacheFile")
        if not idx == int(attrs["cache_file_index"]):
            raise ValueError(
                "These attributes did originate from a different trace in this CacheFile"
            )
        update_trace_attributes(attrs)

    @property
    def origins(self) -> List[str]:
        "returns a list of original files used in creating this cachefile"
        with read_file(self.fname) as f:
            origins = list(f.keys())
        return origins

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


# -----------------------------------------------------------------------------


def update_trace_attributes(attrs: TraceAttributes):
    """overwrite the traceattributes for a trace
    
    the original file and index of the trace are specified as field within the
    TraceAttributes
    args
    ----
    attrs: TraceAttributes
    """
    index: int
    if isindex(attrs["cache_file_index"]):
        index = int(attrs["cache_file_index"])
    else:
        raise ValueError("Index must be an integer")
    fname = attrs["cache_file"]
    attrs = filter_trace_attrs(attrs)

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
                            # attrs = parse_traceattrs(dset.attrs)
                            attrs = asdict(dset.attrs)
                            attrs["origin"] = origin
                            attrs["cache_file"] = str(cf.fname)
                            attrs["cache_file_index"] = str(idx)
                            # check_metadata(str(attrs["readout"]), attrs)
                            return attrs
                        elif what == "data":
                            data = parse_tracedata(dset)
                            return data
                        else:
                            raise NotImplementedError(f"{what} can not be loaded")
                    cnt = ix

    raise IndexError(f"{idx} not in cachefile")


def asdict(attrs: h5py.AttributeManager) -> Dict[str, str]:
    "parse the metadata from a cachefile and return it as dictionary"
    return dict(attrs)


def parse_traceattrs(attrs: h5py.AttributeManager) -> MetaData:
    """parse any metadata from a cachefile and return it as Dict    
    """
    d = dict(attrs)
    for key, val in d.items():
        try:
            d[key] = ast.literal_eval(val)
        except (SyntaxError, ValueError):  # for subject and filedate
            if val == "inf":
                d[key] = inf
            if val == "nan":
                d[key] = nan
            pass
            if key == "xyz_coords":
                xyz = yaml.load("[nan, nan, nan]", Loader=yaml.Loader)
                d[key] = [float(p) for p in xyz]
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
