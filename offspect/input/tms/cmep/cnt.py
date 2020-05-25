# %%
from pathlib import Path
from offspect.cache.file import CacheFile, populate
import matplotlib.pyplot as plt
import numpy as np
from offspect.cache.attrs import AnnotationFactory, decode
from libeep import cnt_file
from math import nan, inf
from ast import literal_eval
from datetime import datetime, timedelta


# %%
def get_recording_start(fname):
    """parse the recording date from the emg filename"""

    parts = Path(fname).stem.split(" ")
    subject = parts[0][0:4]
    recdate = datetime.strptime(parts[1], "%Y-%m-%d_%H-%M-%S")
    return recdate


def load_documentation_txt(fname):
    "load a documentation.txt and return Coords"
    fname = Path(fname).expanduser().absolute()
    if not fname.name == "documentation.txt":
        raise ValueError(f"{fname} is not a valid documentation.txt")

    with fname.open("r") as f:
        lines = f.readlines()
    if lines[-1] != "\n":
        lines.append("\n")  # otherwise, last target is ignored
    coords = dict()
    target = []
    experiment = None
    subject = None
    idx = -1
    malformed = False
    for line in lines:
        # a target block is complete
        if line == "\n":  # a new target block starts
            # make sure everything is from the same experiment and subject
            if subject is None:
                subject = target[-1]
            assert subject == target[-1]
            if experiment is None:
                experiment = target[-2]
            assert experiment == target[-2]

            # make sure the targets are consecutive and monoton
            if int(target[0]) != idx + 2 and not malformed:
                malformed = True
                print(f"{fname} might be malformed due to target #{idx}")

            # parse the target data and add to the dictionary
            # take line four according to documentation,see above
            tmp = ", ".join(target[3].split(" "))
            xyz = literal_eval(f"[{tmp}]")
            timestr = target[4]
            timepoint = datetime.strptime(timestr, "%d.%m.%Y %H:%M:%S")
            target = []
            idx += 1
            # take the last three entries according to documentation,see above
            # correction factor has to be included because the coordinate
            # system of the robot is anchored to the corner of the MNI-space
            # these correction factors have been determined empirically
            # by Felix Quirmbach in May 2020.
            correction = [95.0, -402.0, -132.0]
            coords[timepoint] = [a + b for a, b in zip(xyz[-3:], correction)]

        else:  # info not complete, we need to collect more lines
            target.append(line.strip())
    return coords, subject


# %%
def prepare_annotations(
    fname,
    docname,
    pre_in_ms=100,
    post_in_ms=100,
    select_events=["4"],
    select_channel="Ch1",
    mso=100,
    didt="",
):

    if not Path(fname).with_suffix(".evt").exists():
        raise FileNotFoundError("No matching event file found for", fname)

    coords, subject = load_documentation_txt(docname)
    recstart = get_recording_start(fname)

    cnt = cnt_file(fname)
    fs = cnt.get_sample_frequency()
    pre_in_samples = int(pre_in_ms * fs / 1000)
    post_in_samples = int(post_in_ms * fs / 1000)

    event_samples = []
    event_times = []
    event_names = []
    stimulation_intensity_mso = []
    stimulation_intensity_didt = []
    print(f"Reading events constrained to {select_events}")
    for tix in range(cnt.get_trigger_count()):
        event_name, event_sample, *suppl = cnt.get_trigger(tix)
        if event_name in select_events:
            event_names.append(event_name)
            event_samples.append(event_sample)
            event_time = event_sample / fs
            event_times.append(event_time)
            stimulation_intensity_mso.append(mso)
            stimulation_intensity_didt.append(didt)

    print(f"Assigning coordinates from {docname}")
    xyz_coords = []
    for event_time in event_times:
        event_datetime = recstart + timedelta(seconds=event_time)
        xyz = [nan, nan, nan]
        for idx, (key, _xyz) in enumerate(coords.items()):
            delta = (key - event_datetime).total_seconds()
            if delta > 0:
                xyz = _xyz
                break
        xyz_coords.append(xyz)

    time_since_last_pulse = [a - b for a, b in zip(event_times, [-inf] + event_times)]

    anno = AnnotationFactory(readin="tms", readout="cmep", origin=Path(fname).name)
    anno.set("filedate", str(recstart))
    anno.set("subject", subject)
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", pre_in_samples)
    anno.set("samples_post_event", post_in_samples)
    anno.set("channel_of_interest", [select_channel])
    anno.set("channel_labels", [select_channel])

    # trace fields
    for idx, t in enumerate(event_samples):
        tattr = {
            "id": idx,
            "event_name": event_names[idx],
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": xyz_coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso[idx],
            "stimulation_intensity_didt": stimulation_intensity_didt[idx],
            "reject": False,
            "onset_shift": 0,
        }
        anno.append_trace_attr(tattr)

    return anno.anno


def cut_traces(cntfile, annotation):
    """cut the tracedate from a matfile given Annotations
    args
    ----
    cntfile: FileName
        the cntfile for cutting the data. must correspond in name to the one specified in the annotation
    annotation: Annotations
        the annotations specifying e.g. onsets as well as pre and post durations

    returns
    -------
    traces: List[TraceData]
    """
    cnt = cnt_file(cntfile)
    pre = decode(annotation["attrs"]["samples_pre_event"])
    post = decode(annotation["attrs"]["samples_post_event"])
    cix = [cnt.get_channel_info(c)[0] for c in range(cnt.get_channel_count())].index(
        decode(annotation["attrs"]["channel_of_interest"])[0]
    )
    traces = []
    for attrs in annotation["traces"]:
        onset = decode(attrs["event_sample"])
        trace = cnt.get_samples(fro=onset - pre, to=onset + post)
        trace = np.asanyarray(trace)[:, cix]
        traces.append(trace)
    return traces


if __name__ == "__main__":
    fnames = [
        "/home/rtgugg/Desktop/test-offspect/felix/AmWo/AmWo4a 2019-10-15_15-33-55.cnt",
        "/home/rtgugg/Desktop/test-offspect/felix/AmWo/AmWo4b 2019-10-15_16-37-40.cnt",
    ]
    cfname = "/home/rtgugg/Desktop/test-offspect/felix/file1.hdf5"
    docname = "/home/rtgugg/Desktop/test-offspect/felix/AmWo/documentation.txt"

    pre_in_ms = 100
    post_in_ms = 100
    select_events = ["4"]
    select_channel = "Ch1"
    mso = 100
    didt = ""
    fname = fnames[0]

    # this is where the magic happens
    anno = prepare_annotations(
        fname, docname, pre_in_ms, post_in_ms, select_events, select_channel, mso, didt
    )
    traces = cut_traces(fname, anno)
    populate(cfname, [anno], [traces])
