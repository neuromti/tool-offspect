"""
XDF based protocols
-------------------

This kind of file format is our preferred file format. It is `open-source, well-defined and extensible <https://github.com/sccn/xdf/wiki/Specifications>`_ and has `pxdf <https://pypi.org/project/pyxdf/>`_ to load it with Python. You will need one file.

- :code:`.xdf`

Data
****

The data is espected to have TMS pulses, triggered by spongebob.

"""
from offspect.types import Annotations, FileName
from typing import List, Union, Any, Dict
from liesl.api import XDFFile
from liesl.files.xdf.load import XDFStream
from offspect.types import FileName, Coordinate, MetaData, Annotations, TraceData
from pathlib import Path
from math import nan, inf
import time
import json
import numpy as np
from offspect.cache.attrs import AnnotationFactory, decode
from offspect.protocols.xdf import (
    get_coords_from_xml,
    decode_marker,
    pick_stream_with_channel,
    find_closest_samples,
    yield_timestamps,
    yield_comments,
    list_nan,
    list_nan_coords,
    yield_loc_coords,
    yield_loc_mso,
    yield_loc_didt,
)

# -----------------------------------------------------------------------------


def prepare_annotations(
    xdffile: FileName,
    channel: str,
    pre_in_ms: float,
    post_in_ms: float,
    event_name="Spongebob-Trigger",
    event_mark=1,
    event_stream="Spongebob-Data",
    comment_name=None,
) -> Annotations:
    """ 
    args
    ----

    xdffile: FileName
        the :code:`.xdf`-file with the recorded streams, e.g. data and markers
    channel: str
        which channel to pick
    pre_in_ms: float
        how many ms to cut before the tms
    post_in_ms: float
        how many ms to cut after the tms
    returns
    -------
    annotation: Annotations
        the annotations for this origin files
    """

    # ------------------
    streams = XDFFile(xdffile)
    datastream = pick_stream_with_channel(channel, streams)
    event_stream = streams[event_stream]
    time_stamps = [ts for ts in yield_timestamps(event_stream, event_mark)]
    event_count = len(time_stamps)

    print(f"Found {event_count} events")

    if "reiz_marker_sa" in streams and comment_name is not None:
        comments = [
            c
            for c in yield_comments(
                streams["reiz_marker_sa"],
                time_stamps=time_stamps,
                identifier="stimulus_idx",
                relative="earlier",
            )
        ]
    else:
        comments = ["" for c in time_stamps]

    # global fields
    fs = datastream.nominal_srate
    anno = AnnotationFactory(readin="tms", readout="cmep", origin=Path(xdffile).name)
    anno.set("filedate", time.ctime(Path(xdffile).stat().st_mtime))
    anno.set("subject", "")  # TODO parse from correctly organized file
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", int(pre_in_ms * fs / 1000))
    anno.set("samples_post_event", int(post_in_ms * fs / 1000))
    anno.set("channel_of_interest", channel)
    anno.set("channel_labels", [channel])
    # trace fields
    event_samples = find_closest_samples(datastream, time_stamps)
    event_times = [
        float(t)
        for t in datastream.time_stamps[event_samples] - datastream.time_stamps[0]
    ]
    time_since_last_pulse = [inf] + [
        a - b for a, b in zip(event_times[1:], event_times[0:-1])
    ]

    for idx, t in enumerate(event_samples):
        tattr = {
            "id": idx,
            "event_name": event_stream.name + "-" + str(event_name),
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "comment": comments[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
        }
        anno.append_trace_attr(tattr)
    return anno.anno


def cut_traces(xdffile: FileName, annotation: Annotations) -> List[TraceData]:
    """cut the tracedate from a matfile given Annotations
    args
    ----
    xdfile: FileName
        the xdffile for cutting the data. must correspond in name to the one specified in the annotation
    annotation: Annotations
        the annotations specifying e.g. onsets as well as pre and post durations

    returns
    -------
    traces: List[TraceData]
    """

    streams = XDFFile(xdffile)
    channel = decode(annotation["attrs"]["channel_of_interest"])
    print("Selecting traces for channel", channel)
    datastream = pick_stream_with_channel(channel, streams)
    cix = datastream.channel_labels.index(channel)

    pre = decode(annotation["attrs"]["samples_pre_event"])
    post = decode(annotation["attrs"]["samples_post_event"])
    traces = []
    for attrs in annotation["traces"]:
        onset = decode(attrs["event_sample"])
        trace = datastream.time_series[onset - pre : onset + post, cix]
        traces.append(trace)
    return traces

