"""
Matlab Protocol
---------------

The Matlab format is the oldest kind and mostly from recordings using lz_TMS_v4.m
or lz_TMS_v5.m (see `repository <https://github.com/translationalneurosurgery/load-tms-toolbox>`_). It is based on two files.

- :code:`.mat` storing electrophysiologal data and notes
- :code:`.xml` storing the coordinates of targets

.. note::

   Load the :class:`TraceData` with :func:`~.cut_traces` and the :class:`~.Annotations` with :func:`prepare_annotations`.


Data
****

The :code:`.mat` files contain a single Matlab object. The fields of this object contain the raw EEG and EMG data, and information like channel_names, sampling_rate and raw data_traces. Because it is a Matlab object, it is necessary to load the file with Matlab to recover the data. Afterwards, we can
store the data in a generic format readable by Python. An example how to script
this in Python can be found `here <https://github.com/translationalneurosurgery/stroke-tms-maps/blob/master/intens_tms/clean/_convert_mat.py>`_.

Coordinates
***********

By design, the coordinates of the target-entry pairs were stored  independently from the :code:`mat`-file in an :code:`xml`-file created by localite.  The pairing of coordinates with a specific trace needs to be reconstructed manually (see :ref:`support-link-coords`).  




"""
from typing import List
from pathlib import Path
import datetime
from math import inf, nan
from offspect.types import FileName, Coordinate, MetaData, Annotations, TraceData
from offspect import release
from offspect.cache.attrs import AnnotationFactory, decode
from offspect.protocols.mat import (
    convert_mat,
    get_fs,
    get_onsets,
    get_enames,
    repeat_targets,
    _cut_traces,
    get_coords_from_xml,
)


def prepare_annotations(
    xmlfile: FileName,
    matfile: FileName,
    readout: str,
    channel_of_interest: str,
    pre_in_ms: float,
    post_in_ms: float,
) -> Annotations:
    """load xml and matfile and distill annotations from them

    args
    ----
    xmlfile: FileName
        the xmlfile with the target-entry pairs
    matfile: FileName
        the matfile with the physiological data
    readout: str
        which readout to use (see :data:`~.VALID_READOUTS`
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

    # collect data
    content = convert_mat(matfile)
    # global fields
    origin = Path(matfile).name
    fs = get_fs(content)
    stimulation_intensity_mso = content["mso"][0][0]
    stimulation_intensity_didt = nan
    filedate = str(datetime.datetime(*content["recdate"][0]))

    subject = str(content["subid"][0])
    samples_pre_event = int(pre_in_ms * fs / 1000)
    samples_post_event = int(post_in_ms * fs / 1000)
    # trace fields
    coords = get_coords_from_xml(xmlfile)
    event_samples = get_onsets(content)
    event_times = [o / fs for o in event_samples]
    event_names = get_enames(content)
    time_since_last_pulse = [inf] + [
        a - b for a, b in zip(event_times[1:], event_times[0:-1])
    ]

    anno = AnnotationFactory(readin="tms", readout=readout, origin=origin)
    anno.set("filedate", filedate)
    anno.set("subject", subject)
    anno.set("samplingrate", fs)
    anno.set("samples_pre_event", samples_pre_event)
    anno.set("samples_post_event", samples_post_event)
    anno.set("channel_of_interest", channel_of_interest)
    anno.set("channel_labels", [channel_of_interest])

    for idx, _ in enumerate(event_samples):
        tattr = {
            "id": idx,
            "event_name": f"'{event_names[idx]}'",
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": float(time_since_last_pulse[idx]),
            "stimulation_intensity_mso": float(stimulation_intensity_mso),
            "stimulation_intensity_didt": float(stimulation_intensity_didt),
            "reject": False,
            "comment": "",
            "examiner": "",
            "onset_shift": 0,
        }
        anno.append_trace_attr(tattr)

    return anno.anno


def cut_traces(matfile: FileName, annotation: Annotations) -> List[TraceData]:
    """cut the tracedate from a matfile given Annotations
    args
    ----
    matfile: FileName
        the original matfile. must correspond in name to the one specified in the annotation
    annotation: Annotations
        the annotations specifying e.g. onsets as well as pre and post durations

    returns
    -------
    traces: List[TraceData]
    """
    if Path(matfile).name != annotation["origin"]:
        raise ValueError(
            "Matfile does not correspond with original file. Fix manually if you plan to fork this annotations"
        )
    content = convert_mat(matfile)
    # it is important to decode all values, because they are natively stored as strings only
    target_channel = decode(annotation["attrs"]["channel_of_interest"])
    pre = decode(annotation["attrs"]["samples_pre_event"])
    post = decode(annotation["attrs"]["samples_post_event"])
    onsets = [decode(attr["event_sample"]) for attr in annotation["traces"]]
    traces = _cut_traces(
        content,
        target_channel=target_channel,
        pre_in_samples=pre,
        post_in_samples=post,
        onsets=onsets,
    )
    return traces
