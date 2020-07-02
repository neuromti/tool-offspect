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
import numpy as np
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


def concat_multifile(xdffiles: List[FileName]):
    files = []
    origin = Path(xdffiles[0]).name
    filedate = time.ctime(Path(xdffiles[0]).stat().st_mtime)
    for fname in xdffiles:
        streams = XDFFile(fname)
        files.append(streams)
    return files, origin, filedate


def prepare_annotations_multfile(
    files,
    origin,
    filedate,
    channel: str,
    pre_in_ms: float,
    post_in_ms: float,
    comment_name=None,
):

    # we assume that all mapping was done after any spongebob assessments, 
    # therefore everything earlier than the latest spongebob trigger is 
    # considered irrelevant
    # alternatively, everything in an xdf-file earlier than a reiz_marker of 
    # "" or earlier than any other marker is irrelevant. This is because every 
    # start of a reiz-marker sends out an "" to see whether the marker-server 
    # is running, while for all other assessments but mapping, the reiz-marker 
    # was used to send markers

    for streams in files:
        if streams["reiz_marker_sa"].time_series[-1] == [""]:
            iu1 = 0
        else:
            iu1 = streams["reiz_marker_sa"].time_stamps[-1]

        spbob = np.where(streams["Spongebob-Data"].time_series[:, 11] == 1.0)[0]
        if len(spbob) == 0:  # we never triggered Spongebob in this file
            iu2 = 0
        else:
            idx = spbob[-1]
            iu2 = streams["Spongebob-Data"].time_stamps[idx]
        if max((iu1, iu2)) == 0:
            continue
        else:
            irrelevant_until = max((iu1, iu2))
        print(irrelevant_until)


    # we concatenate the time_series and time_stamps from the multiple xdf \
    # files. Because the clock is continuous and monotonic, we do not need to 
    # correct for any possible reset between xdf files, and gaps are jumped 
    # later
    time_stamps = []
    data_series = None
    data_stamps = None
    for streams in files:
        datastream = pick_stream_with_channel(channel, streams)
        if data_series is None:
            data_series = datastream.time_series
            data_stamps = datastream.time_stamps
        else:
            data_series = np.concatenate((data_series, datastream.time_series), axis=0)
            data_stamps = np.concatenate((data_stamps, datastream.time_stamps), axis=0)

        for event in streams["BrainVision RDA Markers"].time_stamps:
            if event > irrelevant_until:
                time_stamps.append(event)

    event_count = len(time_stamps)
    coords = list_nan_coords(event_count)
    stimulation_intensity_didt = list_nan(event_count)
    stimulation_intensity_mso = list_nan(event_count)
    print(f"Found {event_count} events")
    if event_count == 350:
        grid_layout = "5x7"
        print("This corresponds to a subject with a 5x7 grid")
    elif event_count == 360:
        grid_layout = "6x6"
        print("This corresponds to a subject with a 6x6 grid")
    else:
        grid_layout = "Unknown"
        print("This does not correspond to a known grid layout")

    # global fields
    fs = datastream.nominal_srate
    anno = AnnotationFactory(readin="tms", readout="cmep", origin=origin)
    anno.set("filedate", filedate)
    anno.set("subject", "")  # TODO parse from correctly organized file
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", int(pre_in_ms * fs / 1000))
    anno.set("samples_post_event", int(post_in_ms * fs / 1000))
    anno.set("channel_of_interest", channel)
    anno.set("channel_labels", [channel])
    anno.set("global_comment", f"grid_layout={grid_layout}")
    # trace fields
    event_samples = []
    for ts in time_stamps:
        idx = int(np.argmin(np.abs(data_stamps - ts)))
        event_samples.append(idx)

    #  New Implementation
    # gmfp = np.std(data_series[:, 0:64], 1)
    # artifact = tkeo(gmfp)
    # aptp = []
    # tp = []
    # for onset in event_samples:
    #     hood = gmfp[onset - 50 : onset + 50]
    #     aptp.append(np.max(hood))
    #     tp.append(int(np.argmax(hood) - 50 + onset))
    # event_samples = tp

    gmfp = np.std(data_series[:, 0:64], 1)
    aptp = []
    tp = []
    for onset in event_samples:
        artifact = gmfp[onset - 25 : onset + 25]
        aptp.append(np.ptp(artifact))
        tp.append(int(np.argmax(artifact) - 25 + onset))
    event_samples = tp

    event_times = [float(t) for t in data_stamps[event_samples] - data_stamps[0]]
    time_since_last_pulse = [inf] + [
        a - b for a, b in zip(event_times[1:], event_times[0:-1])
    ]
    for idx, t in enumerate(event_samples):
        tattr = {
            "id": idx,
            "comment": f'{{"artifact_amplitude":{aptp[idx]:3.2f}}}',
            "event_name": "BrainVision RDA Markers - 'S  2'",
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso[idx],
            "stimulation_intensity_didt": stimulation_intensity_didt[idx],
        }
        anno.append_trace_attr(tattr)
    return anno.anno


def cut_traces_multifile(files, annotation: Annotations) -> List[TraceData]:
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

    channel = decode(annotation["attrs"]["channel_of_interest"])
    print("Selecting traces for channel", channel)

    data_series = None
    data_stamps = None
    for streams in files:
        datastream = pick_stream_with_channel(channel, streams)
        cix = datastream.channel_labels.index(channel)
        if data_series is None:
            data_series = datastream.time_series
            data_stamps = datastream.time_stamps
        else:"""
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
import numpy as np
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


def concat_multifile(xdffiles: List[FileName]):
    files = []
    origin = Path(xdffiles[0]).name
    filedate = time.ctime(Path(xdffiles[0]).stat().st_mtime)
    for fname in xdffiles:
        streams = XDFFile(fname)
        files.append(streams)
    return files, origin, filedate


def prepare_annotations_multifile(
    files,
    origin,
    filedate,
    channel: str,
    pre_in_ms: float,
    post_in_ms: float,
    comment_name=None,
):

    # we assume that all mapping was done after any spongebob assessments, 
    # therefore everything earlier than the latest spongebob trigger is 
    # considered irrelevant
    # alternatively, everything in an xdf-file earlier than a reiz_marker of 
    # "" or earlier than any other marker is irrelevant. This is because every 
    # start of a reiz-marker sends out an "" to see whether the marker-server 
    # is running, while for all other assessments but mapping, the reiz-marker 
    # was used to send markers

    for streams in files:
        if streams["reiz_marker_sa"].time_series[-1] == [""]:
            iu1 = 0
        else:
            iu1 = streams["reiz_marker_sa"].time_stamps[-1]

        spbob = np.where(streams["Spongebob-Data"].time_series[:, 11] == 1.0)[0]
        if len(spbob) == 0:  # we never triggered Spongebob in this file
            iu2 = 0
        else:
            idx = spbob[-1]
            iu2 = streams["Spongebob-Data"].time_stamps[idx]

        if iu1 > iu2:
            print("WARNING: Spongebob data was not transmitted after NMES-IOC. Possible reason: Death of Outlet?")
        else:
            print("Spongebob data was transmitted after NMES-IOC")
        if max((iu1, iu2)) == 0:
            continue
        else:
            irrelevant_until = max((iu1, iu2))
        print(irrelevant_until)


    # we concatenate the time_series and time_stamps from the multiple xdf \
    # files. Because the clock is continuous and monotonic, we do not need to 
    # correct for any possible reset between xdf files, and gaps are jumped 
    # later
    time_stamps = []
    data_series = None
    data_stamps = None
    for streams in files:
        datastream = pick_stream_with_channel(channel, streams)
        if data_series is None:
            data_series = datastream.time_series
            data_stamps = datastream.time_stamps
        else:
            data_series = np.concatenate((data_series, datastream.time_series), axis=0)
            data_stamps = np.concatenate((data_stamps, datastream.time_stamps), axis=0)

        for event in streams["BrainVision RDA Markers"].time_stamps:
            if event > irrelevant_until:
                time_stamps.append(event)

    event_count = len(time_stamps)
    coords = list_nan_coords(event_count)
    stimulation_intensity_didt = list_nan(event_count)
    stimulation_intensity_mso = list_nan(event_count)
    print(f"Found {event_count} events")
    if event_count == 350:
        grid_layout = "5x7"
        print("This corresponds to a subject with a 5x7 grid")
    elif event_count == 360:
        grid_layout = "6x6"
        print("This corresponds to a subject with a 6x6 grid")
    else:
        grid_layout = "Unknown"
        print("This does not correspond to a known grid layout")

    # global fields
    fs = datastream.nominal_srate
    anno = AnnotationFactory(readin="tms", readout="cmep", origin=origin)
    anno.set("filedate", filedate)
    anno.set("subject", "")  # TODO parse from correctly organized file
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", int(pre_in_ms * fs / 1000))
    anno.set("samples_post_event", int(post_in_ms * fs / 1000))
    anno.set("channel_of_interest", channel)
    anno.set("channel_labels", [channel])
    anno.set("global_comment", f"grid_layout={grid_layout}")
    # trace fields
    event_samples = []
    for ts in time_stamps:
        idx = int(np.argmin(np.abs(data_stamps - ts)))
        event_samples.append(idx)

    #  New Implementation
    # gmfp = np.std(data_series[:, 0:64], 1)
    # artifact = tkeo(gmfp)
    # aptp = []
    # tp = []
    # for onset in event_samples:
    #     hood = gmfp[onset - 50 : onset + 50]
    #     aptp.append(np.max(hood))
    #     tp.append(int(np.argmax(hood) - 50 + onset))
    # event_samples = tp

    gmfp = np.std(data_series[:, 0:64], 1)
    aptp = []
    tp = []
    for onset in event_samples:
        artifact = gmfp[onset - 25 : onset + 25]
        aptp.append(np.ptp(artifact))
        tp.append(int(np.argmax(artifact) - 25 + onset))
    event_samples = tp

    event_times = [float(t) for t in data_stamps[event_samples] - data_stamps[0]]
    time_since_last_pulse = [inf] + [
        a - b for a, b in zip(event_times[1:], event_times[0:-1])
    ]

    # sometimes, we record way too many pulses for a mapping

    max_allowed_counts = int(360 * 1.2)
    if event_count > max_allowed_counts:
        print("WARNING: There are too many pulses, throwing away possible faulty ones")
        template = np.ones(180)        
        template[0::5] = 1.5
        template[0] = 100
        
        selection = []
        old_xcorr = 0
        new_xcorr = 0
        to = 1 
        fr = 181
        while fr < max_allowed_counts:            
            new_xcorr = np.correlate(time_since_last_pulse[-fr:-to], template)
            print(fr, to, new_xcorr)
            if new_xcorr < old_xcorr/2:
                # the last was a good fit, at least twice better than now
                winner = (fr-1, to-1)
                selection.extend(list(range(to+1, fr+1)))
                fr += 180
                to += 180
                old_xcorr = 0
                new_xcorr = 0
                print("We found a winner", winner)
                
            else:                
                old_xcorr = new_xcorr
                fr += 1
                to += 1
        if len(selection) != 720:
            raise Exception("Did not find a good selection of good events")

        event_samples = drop_selection(event_samples, selection)
        event_times = drop_selection(event_times, selection)
        coords = drop_selection(coords, selection)
        time_since_last_pulse = drop_selection(time_since_last_pulse, selection)
        stimulation_intensity_mso = drop_selection(stimulation_intensity_mso, selection)
        stimulation_intensity_didt = drop_selection(stimulation_intensity_didt, selection)
        aptp = drop_selection(aptp, selection)

    for idx, t in enumerate(event_samples):
        tattr = {
            "id": idx,
            "comment": f'{{"artifact_amplitude":{aptp[idx]:3.2f}}}',
            "event_name": "BrainVision RDA Markers - 'S  2'",
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso[idx],
            "stimulation_intensity_didt": stimulation_intensity_didt[idx],
        }
        anno.append_trace_attr(tattr)
    return anno.anno

def drop_selection(which, selection):
    return [which[idx] for idx in selection]

def cut_traces_multifile(files, annotation: Annotations) -> List[TraceData]:
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

    channel = decode(annotation["attrs"]["channel_of_interest"])
    print("Selecting traces for channel", channel)

    data_series = None
    data_stamps = None
    for streams in files:
        datastream = pick_stream_with_channel(channel, streams)
        cix = datastream.channel_labels.index(channel)
        if data_series is None:
            data_series = datastream.time_series
            data_stamps = datastream.time_stamps
        else:
            data_series = np.concatenate((data_series, datastream.time_series), axis=0)
            data_stamps = np.concatenate((data_stamps, datastream.time_stamps), axis=0)

    pre = decode(annotation["attrs"]["samples_pre_event"])
    post = decode(annotation["attrs"]["samples_post_event"])
    traces = []
    for attrs in annotation["traces"]:
        onset = decode(attrs["event_sample"])
        trace = data_series[onset - pre : onset + post, cix]
        traces.append(trace)
    return traces


# %%


def prepare_annotations(
    streams,
    origin,
    filedate,
    channel: str,
    pre_in_ms: float,
    post_in_ms: float,
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

    datastream = pick_stream_with_channel(channel, streams)

    iu1 = streams["reiz_marker_sa"].time_stamps[-1]
    idx = np.where(streams["Spongebob-Data"].time_series[:, 11] == 1.0)[0][-1]
    iu2 = streams["Spongebob-Data"].time_stamps[idx]
    irrelevant_until = max((iu1, iu2))

    time_stamps = []
    for event in streams["BrainVision RDA Markers"].time_stamps:
        if event > irrelevant_until:
            time_stamps.append(event)

    event_count = len(time_stamps)

    coords = list_nan_coords(event_count)
    stimulation_intensity_didt = list_nan(event_count)
    stimulation_intensity_mso = list_nan(event_count)
    comments = ["" for c in time_stamps]
    print(f"Found {event_count} events")
    if event_count == 350:
        grid_layout = "5x7"
        print("This corresponds to a subject with a 5x7 grid")
    elif event_count == 360:
        grid_layout = "6x6"
        print("This corresponds to a subject with a 6x6 grid")
    else:
        grid_layout = "Unknown"
        print("This does not correspond to a known grid layout")

    # global fields
    fs = datastream.nominal_srate
    anno = AnnotationFactory(readin="tms", readout="cmep", origin=origin)
    anno.set("filedate", filedate)
    anno.set("subject", "")  # TODO parse from correctly organized file
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", int(pre_in_ms * fs / 1000))
    anno.set("samples_post_event", int(post_in_ms * fs / 1000))
    anno.set("channel_of_interest", channel)
    anno.set("channel_labels", [channel])
    anno.set("global_comment", f"grid_layout={grid_layout}")
    # trace fields
    event_samples = find_closest_samples(datastream, time_stamps)

    # shift onset on Peak of artifact
    ephys = streams["BrainVision RDA"]
    gmfp = np.std(ephys.time_series[:, 0:64], 1)
    aptp = []
    tp = []
    for onset in event_samples:
        artifact = gmfp[onset - 25 : onset + 25]
        aptp.append(np.ptp(artifact))
        tp.append(int(np.argmax(artifact) - 25 + onset))
    event_samples = tp

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
            "comment": f'{{"artifact_amplitude":{aptp[idx]:3.2f}}}',
            "event_name": "BrainVision RDA Markers - 'S  2'",
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso[idx],
            "stimulation_intensity_didt": stimulation_intensity_didt[idx],
        }
        anno.append_trace_attr(tattr)
    return anno.anno


def cut_traces(streams, annotation: Annotations) -> List[TraceData]:
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

            data_series = np.concatenate((data_series, datastream.time_series), axis=0)
            data_stamps = np.concatenate((data_stamps, datastream.time_stamps), axis=0)

    pre = decode(annotation["attrs"]["samples_pre_event"])
    post = decode(annotation["attrs"]["samples_post_event"])
    traces = []
    for attrs in annotation["traces"]:
        onset = decode(attrs["event_sample"])
        trace = data_series[onset - pre : onset + post, cix]
        traces.append(trace)
    return traces


# %%


def prepare_annotations(
    streams,
    origin,
    filedate,
    channel: str,
    pre_in_ms: float,
    post_in_ms: float,
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

    datastream = pick_stream_with_channel(channel, streams)

    iu1 = streams["reiz_marker_sa"].time_stamps[-1]
    idx = np.where(streams["Spongebob-Data"].time_series[:, 11] == 1.0)[0][-1]
    iu2 = streams["Spongebob-Data"].time_stamps[idx]
    irrelevant_until = max((iu1, iu2))

    time_stamps = []
    for event in streams["BrainVision RDA Markers"].time_stamps:
        if event > irrelevant_until:
            time_stamps.append(event)

    event_count = len(time_stamps)

    coords = list_nan_coords(event_count)
    stimulation_intensity_didt = list_nan(event_count)
    stimulation_intensity_mso = list_nan(event_count)
    comments = ["" for c in time_stamps]
    print(f"Found {event_count} events")
    if event_count == 350:
        grid_layout = "5x7"
        print("This corresponds to a subject with a 5x7 grid")
    elif event_count == 360:
        grid_layout = "6x6"
        print("This corresponds to a subject with a 6x6 grid")
    else:
        grid_layout = "Unknown"
        print("This does not correspond to a known grid layout")

    # global fields
    fs = datastream.nominal_srate
    anno = AnnotationFactory(readin="tms", readout="cmep", origin=origin)
    anno.set("filedate", filedate)
    anno.set("subject", "")  # TODO parse from correctly organized file
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", int(pre_in_ms * fs / 1000))
    anno.set("samples_post_event", int(post_in_ms * fs / 1000))
    anno.set("channel_of_interest", channel)
    anno.set("channel_labels", [channel])
    anno.set("global_comment", f"grid_layout={grid_layout}")
    # trace fields
    event_samples = find_closest_samples(datastream, time_stamps)

    # shift onset on Peak of artifact
    ephys = streams["BrainVision RDA"]
    gmfp = np.std(ephys.time_series[:, 0:64], 1)
    aptp = []
    tp = []
    for onset in event_samples:
        artifact = gmfp[onset - 25 : onset + 25]
        aptp.append(np.ptp(artifact))
        tp.append(int(np.argmax(artifact) - 25 + onset))
    event_samples = tp

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
            "comment": f'{{"artifact_amplitude":{aptp[idx]:3.2f}}}',
            "event_name": "BrainVision RDA Markers - 'S  2'",
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso[idx],
            "stimulation_intensity_didt": stimulation_intensity_didt[idx],
        }
        anno.append_trace_attr(tattr)
    return anno.anno


def cut_traces(streams, annotation: Annotations) -> List[TraceData]:
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


if __name__ == "__main__":
    
    #folder = "/media/rtgugg/sd/Desktop/test-offspect/betti/nocoords"    
    #fname = "TMS_NMES_AmWo_pre2.xdf"
    #fname = Path(folder) / fname
    #xdf = XDFFile(fname)

    folder = "/media/rtgugg/sd/Desktop/test-offspect/betti/toomanytraces"
    fname = Path(folder) / "TMS_NMES_MaBa_pre2.xdf"
    files = [XDFFile(fname)]