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
    def annotations(self) -> List[dict]:
        "returns a list of annotations within this cachefile"
        return recover_annotations(self)

    @property
    def traces(self) -> List[Tuple[Dict, ndarray]]:
        "return attributes and data for all traces in the file in consecutive fashion"
        return list(self._yield_traces())

    def __str__(self):
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


def recover_annotations(cf: CacheFile) -> List[Dict]:
    """"recover the file and annotations from a cachefile

    args
    ----
    cf: CacheFile
        the cachefile from which to recover

    returns
    -------
    annotations: List[Dict]
        a list of annotations, i.e the metadata of all sourcefiles in the cachefile organized as [sourcesfiles][Dict]
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


def recover_parts(cf: CacheFile) -> Tuple[List[Dict], List[List[ndarray]]]:
    """recover the two parts of a cachefile, i.e. annotations and traces
    
    args
    ----
    cf: CacheFile
        the cachefile from which to recover

    returns
    -------
    annotations: List[Dict]
        a list of annotations, i.e the metadata of all sourcefiles in the cachefile organized as [sourcesfiles][Dict]
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


def populate(
    tf: Union[Path, str], annotations: List[Dict], traceslist: List[List[ndarray]]
) -> str:
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

            for tix, (tattr, trace) in enumerate(zip(settings["traces"], traces)):
                tattr.update(**attrs)
                idx = str(tattr["id"])
                trace = tracegrp.create_dataset(idx, data=trace)
                for k, v in tattr.items():
                    trace.attrs.modify(str(k), str(v))
    return tf.name


def merge(to: Union[str, Path], sources: List[Union[str, Path]]) -> str:
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
    fname = populate(tf=to, annotations=a, traceslist=t)
    return fname

