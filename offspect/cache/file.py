from typing import Union, List, Dict, Tuple
from pathlib import Path
import h5py
import yaml
import numpy as np
from numpy import ndarray
from functools import partial
import ast

VALID_SUFFIX = ".hdf5"

read_file = partial(
    h5py.File, mode="r", libver="latest", swmr=True
)  #: open an hdf5 file in single-write-multiple-reader mode


def check_valid_suffix(fname: Union[Path, str]):
    "check whether the cachefile has a valid suffix"
    fname = Path(fname)
    if fname.suffix != VALID_SUFFIX:
        raise ValueError(f"{fname.suffix} is not a valid cachefile suffix")


class CacheFile:
    """instantiate a new cachefile from HDD
    
    args
    ----
    fname: Union[str, Path]
        path to the file            
    """

    def __init__(self, fname: Union[str, Path]):
        self.fname = Path(fname).absolute().expanduser()
        if self.fname.exists() == False:  # pragma no cover
            raise FileNotFoundError(f"{self.fname} does not exist")
        check_valid_suffix(fname)

    def _yield_trdata(self):
        with read_file(self.fname) as f:
            for origin in f.keys():
                for idx in f[origin]["traces"]:
                    # load data fresh from file
                    f[origin]["traces"][idx].id.refresh()
                    yield parse_trace(f[origin]["traces"][idx])

    def _yield_trattrs(self):
        with read_file(self.fname) as f:
            for origin in f.keys():
                for idx in f[origin]["traces"]:
                    yml = dict()
                    yml["origin"] = origin
                    yml["attrs"] = parse_attrs(f[origin].attrs)
                    dset = f[origin]["traces"][idx]
                    dset.id.refresh()  # load fresh from file
                    yml["trace"] = parse_attrs(dset.attrs)
                    yield yml

    def _yield_traces(self):
        attrs = self._yield_trattrs()
        traces = self._yield_trdata()
        while True:
            try:
                a = next(attrs)
                t = next(traces)
                yield (a, t)
            except StopIteration:
                return

    @property
    def origins(self) -> List[str]:
        "returns a list of original files used in creating this cachefile"
        with read_file(self.fname) as f:
            origins = list(f.keys())
        return origins

    @property
    def traces(self) -> List[Tuple[Dict, ndarray]]:
        "return attributes and data for all traces in the file in consecutive fashion"
        return list(self._yield_traces())


def parse_attrs(attrs: h5py.AttributeManager) -> Dict:
    "parse attributes from a cachefile and return it as dictionary"
    d = dict(attrs)
    for key, val in d.items():
        try:
            d[key] = ast.literal_eval(val)
        except (SyntaxError, ValueError):  # for subject and filedate
            pass
    return d


def parse_trace(dset: h5py.Dataset) -> ndarray:
    "parse a cachefile dataset and return it as a trace"
    return np.asanyarray(dset, dtype=float)


def recover_parts(cf: CacheFile) -> Tuple[List[Dict], List[List[ndarray]]]:
    """recover the two parts of a cachefile, i.e. events and traces
    
    args
    ----
    cf: CacheFile
        the cachefile from which to recover

    returns:
    events: List[Dict]
        a list of dictionary of the metadata of all sourcefiles in the cachefile organized as [sourcesfiles][Dict]
    traces: List[List[ndarray]]
        a list of the traces of all sourcefiles saved in the cachefile 
        organized as [sourcefiles][traces][ndarray-data]

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


def merge(dest: Union[str, Path], sources: List[Union[str, Path]]):
    sources = [Path(source).expanduser().absolute() for source in sources]
    dest = Path(dest).expanduser().absolute()
    if dest.exists():
        raise FileExistsError(f"{dest.name} already exists")
    check_valid_suffix(dest)

    e: List[Dict] = []
    t: List[ndarray] = []
    for source in sources:
        events, traces = recover_parts(CacheFile(source))
