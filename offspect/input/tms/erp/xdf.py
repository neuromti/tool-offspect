"""
TMS-ERP for XDF based protocols
-------------------------------
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
    yield_comments,
    yield_timestamps,
    list_nan_coords,
    list_nan,
)

# -----------------------------------------------------------------------------
def get_datastream(streams: XDFFile, channels: List[str]) -> XDFStream:
    datastreams = set(pick_stream_with_channel(chan, streams) for chan in channels)
    assert len(datastreams) == 1
    return datastreams.pop()


def prepare_annotations(
    xdffile: FileName,
    stream_of_interest: str,
    pre_in_ms: float,
    post_in_ms: float,
    xmlfile: FileName = None,
    event_stream: str = "localite_marker",
    event_name: Union[str, int] = "coil_0_didt",
) -> Annotations:
    """load a documentation.txt and cnt-files and distill annotations from them
    
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
    streams = XDFFile(xdffile)
    if stream_of_interest in streams:
        datastream = streams[stream_of_interest]
    else:
        raise KeyError(f"Stream {stream_of_interest} was not found in the data")

    event_stream = streams[event_stream]
    time_stamps = [ts for ts in yield_timestamps(event_stream, event_name)]
    event_count = len(time_stamps)

    if "localite_flow" in streams or "localite_marker" in streams:
        print("Not implemented, but here we could parse coords and intensity")
    else:
        coords = list_nan_coords(event_count)
        stimulation_intensity_didt = list_nan(event_count)
        stimulation_intensity_mso = list_nan(event_count)

    if "reiz_marker_sa" in streams:
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
    anno = AnnotationFactory(readin="tms", readout="erp", origin=Path(xdffile).name)
    anno.set("filedate", time.ctime(Path(xdffile).stat().st_mtime))
    anno.set("subject", "")  # TODO parse from somewhere
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", int(pre_in_ms * fs / 1000))
    anno.set("samples_post_event", int(post_in_ms * fs / 1000))
    anno.set("channel_of_interest", datastream.name)
    anno.set("channel_labels", datastream.channel_labels)
    # trace fields
    event_samples = find_closest_samples(datastream, time_stamps)
    event_times = [
        float(t)
        for t in datastream.time_stamps[event_samples] - datastream.time_stamps[0]
    ]
    time_since_last_pulse = [inf] + [
        a - b for a, b in zip(event_times[1:], event_times[0:-1])
    ]

    for idx in range(event_count):
        tattr = {
            "id": idx,
            "event_name": event_stream + str(event_name),
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso[idx],
            "stimulation_intensity_didt": stimulation_intensity_didt[idx],
            "comment": comments[idx],
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
    soi = decode(annotation["attrs"]["channel_of_interest"])
    print("Selecting traces for stream", soi)
    datastream = streams[soi]

    pre = decode(annotation["attrs"]["samples_pre_event"])
    post = decode(annotation["attrs"]["samples_post_event"])
    traces = []
    for attrs in annotation["traces"]:
        onset = decode(attrs["event_sample"])
        trace = datastream.time_series[onset - pre : onset + post, :]
        traces.append(trace)
    return traces
