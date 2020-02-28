from typing import Union, List, Dict, Tuple
from pathlib import Path
import h5py
import yaml
import numpy as np
from numpy import ndarray
from functools import partial

VALID_SUFFIX = ".hdf5"

read_file = partial(h5py.File, mode="r", libver="latest", swmr=True)


def _get_cachefile_template() -> List[Dict]:
    with (Path(__file__).parent / "cache_template.yml").open("r") as f:
        settings = f.read()
    ymls = list(yaml.load_all(settings, Loader=yaml.Loader))
    return ymls


def create_test_cachefile(fname: Union[str, Path], settings: str = None) -> Path:
    """create a cachefile for testing and development

    args
    ----
    fname: Union[str, Path]
        the path to the to be created file. Will raise an exception if the file already exists
    settings: str
        a yaml formatted string with the attributes for the cachefile
        defaults to None, and will then read from default template

    returns
    -------
    fname: Path
        the path to the newly created cachefile
    """

    # load the default settings if not set
    if settings is None:
        ymls = _get_cachefile_template()
    else:
        ymls = list(yaml.load_all(settings, Loader=yaml.Loader))

    # check whether the filename conforms
    tf = Path(fname).absolute().expanduser()
    if tf.exists():
        raise FileExistsError(f"{tf.name} already exists")
    check_valid_suffix(tf)

    # populate the cachefile
    with h5py.File(tf, "w") as f:
        for yml in ymls:
            ofile = f.create_group(yml["origin"])
            # fill with ofile-attributes
            attrs = yml["attrs"]
            for key, val in attrs.items():
                ofile.attrs.modify(str(key), str(val))
            # fill with traces and trace-attributes
            traces = ofile.create_group("traces")
            samples = (
                yml["attrs"]["samples_pre_event"] + yml["attrs"]["samples_post_event"]
            )
            channels = len(yml["attrs"]["channel_labels"])
            for tix, tattr in enumerate(yml["traces"]):
                data = np.ones((samples, channels)) * tix
                idx = str(tattr["id"])
                trace = traces.create_dataset(idx, data=data)
                for k, v in tattr.items():
                    trace.attrs.modify(str(k), str(v))
    return fname


def check_valid_suffix(fname: Path):
    "check whether the cachefile has a valid suffix"
    if fname.suffix != VALID_SUFFIX:
        raise ValueError(f"{fname.suffix} is not a valid cachefile suffix")


class CacheFile:
    def __init__(self, fname: Union[str, Path]):
        self.fname = Path(fname).absolute().expanduser()
        if self.fname.exists() == False:
            raise FileNotFoundError(f"{self.fname} does not exist")
        check_valid_suffix(fname)

    @property
    def origins(self):
        with read_file(self.fname) as f:
            origins = list(f.keys())
        return origins

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
    def traces(self) -> List[Tuple[Dict, ndarray]]:
        "return attributes and data for all traces in the file"
        return list(self._yield_traces())

