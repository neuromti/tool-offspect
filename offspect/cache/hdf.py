from typing import Union
from pathlib import Path
import h5py
import yaml
import numpy as np


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
        with (Path(__file__).parent / "cache_template.yml").open("r") as f:
            settings = f.read()
    ymls = list(yaml.load_all(settings, Loader=yaml.Loader))

    # check whether the filename conforms
    tf = Path(fname).absolute().expanduser()
    if tf.exists():
        raise FileExistsError(f"{tf.name} already exists")
    if tf.suffix != ".hdf5":
        raise ValueError(f"{tf.suffix} is not a valid cachefile suffix")

    # populate the cachefile
    with h5py.File(tf, "w") as f:
        for yml in ymls:
            ofile = f.create_group(yml["origin"])
            # fill with ofile-attributes
            attrs = yml["attrs"]
            for key, val in attrs.items():
                ofile.attrs.modify(key, val)
            # fill with traces and trace-attributes
            traces = ofile.create_group("traces")
            samples = (
                yml["attrs"]["samples_pre_event"] + yml["attrs"]["samples_post_event"]
            )
            channels = len(yml["attrs"]["channel_labels"])
            for tix, tattr in enumerate(yml["traces"]):
                data = np.ones((samples, channels)) * tix
                idx = str(tattr["id"])
                traces.create_dataset(idx, data=data)
    return fname


class CacheFile:
    def __init__(self, fname: Union[str, Path]):
        self.fname = Path(fname).absolute().expanduser()
        if self.fname.exists() == False:
            raise FileNotFoundError(f"{self.fname} does not exist")
        if self.fname.suffix != ".hdf5":
            raise ValueError(f"{self.fname} has invalid file type")

        with h5py.File(self.fname, "r") as f:
            origins = f.keys()
            for origin in origins:
                traces = f[origin].keys()

    @property
    def origins(self):
        with h5py.File(self.fname, "r") as f:
            origins = f.keys()
        return list(origins)
