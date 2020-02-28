from typing import List, Union, Dict
from pathlib import Path
import h5py
import yaml
import numpy as np


def get_cachefile_template() -> List[Dict]:
    with (Path(__file__).parent / "cache_template.yml").open("r") as f:
        settings = f.read()
    settings = list(yaml.load_all(settings, Loader=yaml.Loader))
    return settings


def create_test_cachefile(fname: Union[str, Path], settings: dict) -> Path:
    """create a cachefile for testing and development

    args
    ----
    fname: Union[str, Path]
        the path to the to be created file. Will raise an exception if the file already exists
    settings: dict
        a yaml-compatible dictionary with the attributes for the cachefile.

    returns
    -------
    fname: Path
        the path to the newly created cachefile
    """

    # check whether the filename conforms
    tf = Path(fname).absolute().expanduser()
    if tf.exists():
        raise FileExistsError(f"{tf.name} already exists")

    # populate the cachefile
    with h5py.File(tf, "w") as f:
        ofile = f.create_group(settings["origin"])
        # fill with ofile-attributes
        attrs = settings["attrs"]
        for key, val in attrs.items():
            ofile.attrs.modify(str(key), str(val))
        # fill with traces and trace-attributes
        traces = ofile.create_group("traces")
        samples = (
            settings["attrs"]["samples_pre_event"]
            + settings["attrs"]["samples_post_event"]
        )
        channels = len(settings["attrs"]["channel_labels"])
        for tix, tattr in enumerate(settings["traces"]):
            data = np.ones((samples, channels)) * tix
            idx = str(tattr["id"])
            trace = traces.create_dataset(idx, data=data)
            for k, v in tattr.items():
                trace.attrs.modify(str(k), str(v))
    return fname

