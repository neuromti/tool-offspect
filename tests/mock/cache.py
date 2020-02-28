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


def create_test_cachefile(fname: Union[str, Path], settings: List[dict]) -> Path:
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

    # check whether the filename conforms
    tf = Path(fname).absolute().expanduser()
    if tf.exists():
        raise FileExistsError(f"{tf.name} already exists")

    # populate the cachefile
    with h5py.File(tf, "w") as f:
        for yml in settings:
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

