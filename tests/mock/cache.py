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


def create_fake_trace(
    neg_peak_magnitude_uv: float = -20.8,
    neg_peak_latency_ms: float = 16.2,
    pos_peak_magnitude_uv: float = 32.6,
    pos_peak_latency_ms: float = 32.7,
    zcr_latency_ms: float = 23.4,
    samplingrate: int = 1000,
    samples_pre_event: int = 1000,
    samples_post_event: int = 1000,
    channel_labels: List[str] = ["EDC_L"],
    **kwargs,
):
    samples = samples_pre_event + samples_post_event
    channels = len(channel_labels)

    xraw = [
        zcr_latency_ms - neg_peak_latency_ms,
        neg_peak_latency_ms,
        zcr_latency_ms,
        pos_peak_latency_ms,
        pos_peak_latency_ms + zcr_latency_ms,
    ]
    x = [x + samples_pre_event * samplingrate / 1000 for x in xraw]
    y = [0, neg_peak_magnitude_uv, 0, pos_peak_magnitude_uv, 0]
    win = np.hanning(25 * samplingrate / 1000)
    win = win / sum(win)

    ax = [x + samples_pre_event * samplingrate / 1000 for x in [-1, 0, 1, 5]]

    traces = []
    for chan in range(channels):
        trace = np.interp(np.arange(samples), x, y)
        trace = np.convolve(trace, win, "same")
        ay = np.random.lognormal(4, 0.3, 4) * ([0, 1, -1, 0])
        trace += np.interp(np.arange(samples), ax, ay)
        traces.append(trace)
    traces = np.asanyarray(traces).T
    return traces


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

        for tix, tattr in enumerate(settings["traces"]):
            tattr.update(**attrs)
            data = create_fake_trace(**tattr)
            idx = str(tattr["id"])
            trace = traces.create_dataset(idx, data=data)
            for k, v in tattr.items():
                trace.attrs.modify(str(k), str(v))
    return fname

