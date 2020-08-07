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
from json.decoder import JSONDecodeError
import numpy as np
from offspect.types import Annotations, FileName
from typing import List, Union, Any, Dict
from liesl.api import XDFFile
from liesl.files.xdf.load import XDFStream
from offspect.types import (
    FileName,
    Coordinate,
    MetaData,
    Annotations,
    TraceData,
)
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
    targets=[[-36.6300, -17.6768, 54.3147], [36.6300, -17.6768, 54.3147]],
):

    # we assume that all mapping was done after any spongebob assessments,
    # therefore everything earlier than the latest spongebob trigger is
    # considered irrelevant
    # alternatively, everything in an xdf-file earlier than a reiz_marker of
    # "" or earlier than any other marker is irrelevant. This is because every
    # start of a reiz-marker sends out an "" to see whether the marker-server
    # is running, while for all other assessments but mapping, the reiz-marker
    # was used to send markers

    irrelevant_until = 0
    for streams in files:
        if "localite_marker" in streams.keys():
            for mrk, ts in zip(
                streams["localite_marker"].time_series,
                streams["localite_marker"].time_stamps,
            ):
                if mrk == ["Starte Hotspotsuche"]:
                    iu1 = ts
                    print("Detected Start of Hotspot search, so NMES was over")
        else:
            if streams["reiz_marker_sa"].time_series[-1] == [""]:
                iu1 = 0
            else:
                iu1 = streams["reiz_marker_sa"].time_stamps[-1]
                print("Detected any reiz_marker, and used the last event")

        if iu1 == 0:
            continue
        else:
            irrelevant_until = iu1
        print(irrelevant_until)

    # we concatenate the time_series and time_stamps from the multiple xdf \
    # files. Because the clock is continuous and monotonic, we do not need to
    # correct for any possible reset between xdf files, and gaps are jumped
    # later
    time_stamps = []
    lucky_phase = []
    data_series = None
    data_stamps = None
    # if in all files there is a localite-marker stream then initalize
    # collection over those files

    for streams in files:
        datastream = pick_stream_with_channel(channel, streams)
        if data_series is None:
            data_series = datastream.time_series
            data_stamps = datastream.time_stamps
        else:
            data_series = np.concatenate(
                (data_series, datastream.time_series), axis=0
            )
            data_stamps = np.concatenate(
                (data_stamps, datastream.time_stamps), axis=0
            )

        # channel 9 of spongebob contains the current phase in rad
        # channel 11 of spongebob contains trigger out
        # because we need to send a command to spongebob to trigger, and
        # because there are only two tasks where we used the luckyloop, i.e.
        # either pdNMES or pdTMS, and because anything later than
        # `irrelevant_until` occured after pdNMES, these events can only come
        # from pdTMS.
        for phase, stimulus, event in zip(
            streams["Spongebob-Data"].time_series[:, 9],
            streams["Spongebob-Data"].time_series[:, 11],
            streams["Spongebob-Data"].time_stamps,
        ):
            if event > irrelevant_until:
                if stimulus > 0:
                    time_stamps.append(event)
                    lucky_phase.append(phase)

    # within a block, all stimuli follow roughly 4-5s after the next
    # between blocks, there is a longer break aroung 9-10s
    # the first pdTMS at 100%MSO  occurs after the second 10pulse block
    # from the IOC curves. Please note, that sometimes, blocks lasts one
    # to two stimuli more or less due to technical issues
    # we expect that a full measurement resulted in around 760 stimuli
    first_time_stamps = []
    second_time_stamps = []
    first_targets = []
    second_targets = []
    first_phase, second_phase = [], []
    if len(time_stamps) < 0.9 * 760:
        print(
            f"Only {len(time_stamps)} events is too few, likely only one hemisphere was completed."
        )
    else:
        # if we have enough events, we likely measured both hemispheres.
        # usually the longest break was between hemispheres, but not always!
        # therefore, we try to find the longest break closest to the middle of
        # the measurement
        time_delta = np.gradient(time_stamps)
        offset = (
            len(time_delta) // 2 - 90
        )  # shortly before the expected middle of the measurement
        longest_break = np.argmax(time_delta[offset : offset + 180]) + offset

        # first_hemisphere occured before the longer break
        first_time_stamps = time_stamps[longest_break - 50 : longest_break]
        first_onset = np.argmax(np.gradient(first_time_stamps))
        first_time_stamps = first_time_stamps[first_onset:]
        first_phase = lucky_phase[
            longest_break - 50 + first_onset : longest_break
        ]
        print(f"Found {len(first_time_stamps)} stimuli for first hemisphere")
        first_targets = [targets[0]] * len(first_time_stamps)
    if len(time_stamps) < 0.9 * 380:
        print(
            f"Only {len(time_stamps)} events is too few, likely not even one hemisphere was completed."
        )
    else:
        # second hemisphere occured at the end of all pd stimuli
        second_time_stamps = time_stamps[-50:]
        second_onset = np.argmax(np.gradient(second_time_stamps))
        second_time_stamps = second_time_stamps[second_onset:]
        second_phase = lucky_phase[-50 + second_onset :]
        print(f"Found {len(second_time_stamps)} stimuli for second hemisphere")
        second_targets = [targets[1]] * len(second_time_stamps)

    time_stamps = first_time_stamps + second_time_stamps
    coords = first_targets + second_targets
    target_phase = first_phase + second_phase

    # prepare filling the annotations
    event_count = len(time_stamps)
    stimulation_intensity_didt = list_nan(event_count)
    stimulation_intensity_mso = ["100"] * event_count
    print(f"Found {event_count} events in total")

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
    anno.set("global_comment", "")
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

    # shift the tms onset to the artifact
    gmfp = np.std(data_series[:, 0:64], 1)
    aptp = []
    tp = []
    for onset in event_samples:
        artifact = gmfp[onset - 25 : onset + 25]
        aptp.append(np.ptp(artifact))
        tp.append(int(np.argmax(artifact) - 25 + onset))
    event_samples = tp

    event_times = [
        float(t) for t in data_stamps[event_samples] - data_stamps[0]
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
            "target_phase": str(target_phase[idx]),
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
        else:
            data_series = np.concatenate(
                (data_series, datastream.time_series), axis=0
            )
            data_stamps = np.concatenate(
                (data_stamps, datastream.time_stamps), axis=0
            )

    pre = decode(annotation["attrs"]["samples_pre_event"])
    post = decode(annotation["attrs"]["samples_post_event"])
    traces = []
    for attrs in annotation["traces"]:
        onset = decode(attrs["event_sample"])
        trace = data_series[onset - pre : onset + post, cix]
        traces.append(trace)
    return traces


if __name__ == "__main__":
    from offspect.cache.file import populate

    folder = "//media/rtgugg/sd/Desktop/test-offspect/betti/pd-mso100"
    # fname = Path(folder) / "TMS_NMES_PoHe_post3.xdf"
    fname = Path(folder) / "TMS_NMES_AuWi_pre4.xdf"
    cfname = str(Path(folder) / "TMS_NMES_AuWi_pre4.hdf5")
    files, origin, filedate = concat_multifile([str(fname)])
    channel = "EDC_L"
    pre_in_ms = 150
    post_in_ms = 150
    comment_name = None

    anno = prepare_annotations_multifile(
        files=files,
        origin=origin,
        filedate=filedate,
        channel=channel,
        pre_in_ms=pre_in_ms,
        post_in_ms=post_in_ms,
        comment_name=comment_name,
        targets=[[-36.6300, -17.6768, 54.3147], [36.6300, -17.6768, 54.3147]],
    )
    traces = cut_traces_multifile(files, annotation=anno)
    populate(cfname, [anno], [traces])

