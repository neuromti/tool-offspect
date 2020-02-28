from typing import Union, List, Dict, Tuple
from pathlib import Path
import h5py
import yaml
import numpy as np
from numpy import ndarray
from functools import partial

VALID_SUFFIX = ".hdf5"

read_file = partial(
    h5py.File, mode="r", libver="latest", swmr=True
)  #: open an hdf5 file in single-write-multiple-reader mode


def check_valid_suffix(fname: Path):
    "check whether the cachefile has a valid suffix"
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
        if self.fname.exists() == False:
            raise FileNotFoundError(f"{self.fname} does not exist")
        check_valid_suffix(fname)

    def _yield_trdata(self):
        with read_file(self.fname) as f:
            for origin in f.keys():
                for idx in f[origin]["traces"]:
                    dset = f[origin]["traces"][idx]
                    dset.id.refresh()  # load data fresh from file
                    yield np.asanyarray(dset, dtype=float)

    def _yield_trattrs(self):
        with read_file(self.fname) as f:
            for origin in f.keys():
                for idx in f[origin]["traces"]:
                    yml = dict()
                    yml["origin"] = origin
                    yml["attrs"] = dict(f[origin].attrs)
                    dset = f[origin]["traces"][idx]
                    dset.id.refresh()  # load fresh from file
                    tattrs = dict(dset.attrs)
                    yml["trace"] = tattrs
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
        "return attributes and data for all traces in the file"
        return list(self._yield_traces())

