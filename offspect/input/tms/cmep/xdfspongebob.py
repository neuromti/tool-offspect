"""
XDF based protocols
-------------------

This kind of file format is our preferred file format. It is `open-source, well-defined and extensible <https://github.com/sccn/xdf/wiki/Specifications>`_ and has `pxdf <https://pypi.org/project/pyxdf/>`_ to load it with Python. You will need one file.

- :code:`.xdf`

Data
****

Because LabRecorder can record multiple streams into a single :code:`.xdf`-file. These files can contain therefore not only EEG and EMG, but also e.g. pupilometric data, respiration effort, grip force, and many more. As it allows to record multiple streams, it also offers the option to record coordinates (as e.g. sent with every pulse from localite version 4.0) together with the raw data (as sent e.g. by eego or bvr) and additional markers. 

Coordinates
***********

In the optimal case, the :code:`.xdf`-file contains already sufficient information about the coordinates, and pairing is automatic. Yet, there will be some :code:`.xdf`-files, where not all streams were recorded. This might have happened e.g. due to errors in the recording script, an erroneous automated recording, or during manual recording with LabRecorder. In these cases, information about coordinates or other markers can be missing. The pairing of coordinates with a specific trace needs to be reconstructed manually (see :ref:`support-link-coords`).
 
If multiple protocols were recorded in one :code:`xdf`-file, as often happened during manual recording, we will have hundreds of stimuli. Worse, it can be that even marker-streams are missing, and there is no information when a protocol started within the long recording. Linking them to the correct coordinates is tricky, and the best chance is probably taking account of the relative latency between subsequent stimuli.

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
    xmlfile: FileName = None,
    event_name="coil_0_didt",
    event_mark="coil_0_didt",
    event_stream="localite_marker",
    comment_name=None,
) -> Annotations:
    """load a documentation.txt and cnt-files and distill annotations from them
    
    args
    ----
    xmlfile: FileName
        an option xml file with information about the target coordinates 

    readout: str
        which readout to use
    channel: str
        which channel to pick
    pre_in_ms: float
        how many ms to cut before the tms
    post_in_ms: float
        how many ms to cut after the tms
    xdffile: FileName
        the :code:`.xdf`-file with the recorded streams, e.g. data and markers
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

    if (("localite_flow" in streams or "localite_marker") in streams) and not("Spongebob-Data" in streams):
        loc_stream = streams["localite_marker"]
        coords = list(yield_loc_coords(loc_stream, time_stamps))
        stimulation_intensity_didt = list(yield_loc_didt(loc_stream, time_stamps))
        stimulation_intensity_mso = list(yield_loc_mso(loc_stream, time_stamps))
    else:
        coords = list_nan_coords(event_count)
        stimulation_intensity_didt = list_nan(event_count)
        stimulation_intensity_mso = list_nan(event_count)
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
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso[idx],
            "stimulation_intensity_didt": stimulation_intensity_didt[idx],
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
#%%

if __name__ == "__main__":
    filename = "/home/juli/acute_study/recordings/NoDi/IMONAS-acute-study-intervention_R001.xdf"
    anno = prepare_annotations(
            xdffile = filename,
            channel = "EDC_R",
            pre_in_ms = 100,
            post_in_ms = 100,
            event_stream="Spongebob-Data",
            event_mark = 1,
            event_name = "Spongebob-Trigger",
            comment_name="Stimulus comment"
            )
    traces = cut_traces(xdffile, anno)
