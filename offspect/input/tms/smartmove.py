"""
Smartmove robotic
-----------------

These recordings come from the `smartmove robotic TMS <https://www.ant-neuro.com/products/smartmove>`_. This input format uses three files:

- :code:`.cnt` for EEG
- :code:`.cnt` for EMG
- :code:`.txt` for Coordinates


.. note::

   Load the :class:`TraceData` with :func:`~.load_ephys_file` and the :class:`Coords` with :func:`load_documentation_txt`


Data
****

EEG and EMG data is stored in the native file-format of the eego recording software. It can be loaded with `libeep <https://github.com/translationalneurosurgery/libeep>`_. During robotic TMS, the 64 EEG channels and the 8 EMG channels are stored in
separate :code:`.cnt` files.  

Coordinates
***********


During the mapping procedure, the coordinates of the target positions, i.e. where the robot will be moved to, are saved in a :code:`documentation.txt`-file. Please note that these are the targets for the robotic movement, 
recorded, not the actual coordinates of stimulation. The actual coordinates at the time of stimulation do not appear to have been stored at all. 

.. admonition:: Documentation.txt

    The file documentation.txt stores the coordinates of each target the robot arm moved to. It does not contain information regarding manual adjustments (i.e. adjusting distance of coil to the head) or the actual coil position at the time of stimulation. Target coordinates are given in medical image coordinates (CT / 3D image).

    - Target counter: Counts the number of successfully reached targets, including this one. 
    - Target number: Point number in the total list of all targets.
    - Target label: The ‘name’ of the target point. Usually the same as the target number.
    - X-vector [<m11> <m21> <m31>]
    - Y-vector [<m12> <m22> <m32>]
    - Z-vector [<m13> <m23> <m33>]
    - Position [<x> <y> <z>]
    - Date & time point [dd.mm.yy hh:mm:ss]
    - Experiment name [always ‘TMS exp’]
    - Subject ID [NnVv]


The coordinates of the targets are stored in one or multiple :code:`targets_*.sav`-files in xml format. The filename of this save
file encodes experiment, subject pseudonym, date and hour, e.g.:
:code:`targets_<experiment>_<VvNn>_20190603_1624.sav`. These coordinates are the e.g. the grid of targets predefined before starting the mapping.


The file success.txt stores the coordinates of only the last target the robot arm moved to. The first line reads ‘success’ (move ended at desired position), ‘start’ (move started but not ended) or ‘fail’ (move ended before reaching the target due to error). The second line contains the timestamp of when the status was updated. For line 4 to 10, same notation as in documentation.txt.

The file target_TMS_exp_[NnVv]_[yyyymmdd_hhmm] stores the coordinates of all created targets. It contains the position (<x>, <y> and <z>), matrix operations (<m11>, <m12>... until <m33>) and target label (<label>), each labeled as such.


Module Content
**************

"""
from offspect import release
from offspect.types import FileName, Coordinate, TraceData, Annotations, MetaData
from pathlib import Path
from ast import literal_eval
from typing import List, Tuple, Dict, Generator, Any
from datetime import datetime
import numpy as np
from math import inf, nan
from offspect.cache.check import VALID_READOUTS, SPECIFIC_TRACEKEYS

from os import environ

if not environ.get("READTHEDOCS", False):
    from libeep import cnt_file


def load_documentation_txt(fname: FileName) -> Dict[int, Coordinate]:
    "load a documentation.txt and return Coords"
    fname = Path(fname).expanduser().absolute()
    if not fname.name == "documentation.txt":
        raise ValueError(f"{fname} is not a valid documentation.txt")

    with fname.open("r") as f:
        lines = f.readlines()
    lines.append("\n")  # otherwise, last target is ignored
    coords = dict()
    target: List[str]
    target = []
    experiment = None
    subject = None
    idx = -1
    for line in lines:
        # a target block is complete
        if line == "\n":
            # make sure everything is from the same experiment and subject
            if subject is None:
                subject = target[-1]
            assert subject == target[-1]
            if experiment is None:
                experiment = target[-2]
            assert experiment == target[-2]

            # make sure the targets are consecutive and monoton
            if int(target[0]) != idx + 2:
                raise ValueError(f"{fname} is malformed")

            # parse the target data and add to the dictionary
            # take line four according to documentation,see above
            tmp = ", ".join(target[3].split(" "))
            xyz = literal_eval(f"[{tmp}]")
            target = []
            idx += 1
            # take the last three entries according to documentation,see above
            coords[idx] = xyz[-3:]

        else:  # info not complete, we need to collect more lines
            target.append(line.strip())
    return coords


def is_eegfile_valid(fname: FileName) -> bool:
    try:
        assert Path(fname).suffix == ".cnt"
        parts = Path(fname).stem.split("_")  # stem, so without the suffix
        # make sure both subject names are the same
        assert parts[0] == parts[1]
        subject = parts[0]
        assert len(subject) == 4
        assert subject[0::2].isupper()
        assert subject[1::2].islower()
        return True
    except AssertionError:
        return False


def is_eeg_file(fname: FileName) -> bool:
    "return true if this is the eeg-file"
    parts: List[str] = Path(fname).stem.split("_")
    # VvNn_VvNn_YYYY-MM-DD_HH-MM-SS.cnt
    return parts[0] == parts[1]


def parse_recording_date(fname: FileName) -> datetime:
    """
    The  eeg cnt-file should have the following format: 
    VvNn_VvNn_YYYY-MM-DD_HH-MM-SS.cnt
    """
    parts: List[str] = []
    for part in Path(fname).stem.split("_"):
        parts += part.split(" ")
    delements = parts[-2].split("-") + parts[-1].split("-")
    return datetime(*(int(d) for d in delements))  # type: ignore


def load_triggers(fname: FileName) -> List[Tuple[str, int]]:
    c = cnt_file(fname)
    triggers = [c.get_trigger(i) for i in range(c.get_trigger_count())]

    events = []
    for t in triggers:
        m = t[0]
        idx = t[1]
        events.append((m, idx))
    return events


def assert_equal_recording_day(eeg_fname: FileName, emg_fname: FileName):
    eeg_day = parse_recording_date(eeg_fname)
    emg_day = parse_recording_date(emg_fname)
    assert eeg_day.year == emg_day.year
    assert eeg_day.month == emg_day.month
    assert eeg_day.day == emg_day.day


def load_ephys_file(
    eeg_fname: FileName,
    emg_fname: FileName,
    pre_in_ms: float = 100,
    post_in_ms: float = 100,
    select_events: List[str] = ["0001"],
    select_channel: str = "Ch1",
) -> Dict[str, Any]:
    """load the electophysiological data for a specific channel for a smartmove file-pair

    args
    ----
    eeg_fname: FileName
        the path to the EEG file. The file is expected to have the following format: VvNn_VvNn_YYYY-MM-DD_HH-MM-SS.cnt
    emg_fname: FileName
        the path to the EMG file. The  file is expected to have the following format: VvNn<qualifier> YYYY-MM-DD_HH-MM-SS.cnt
    pre_in_ms: float = 100
        how much time before the TMS
    post_in_ms: float = 100
        how much time after the TMS
    select_events: List[str] = ["0001"]
        which events indicate the occurence of a TMS-pulse
    select_channel: str = "Ch1"
        the channel to use. Note that EMG channel labes only offer a selection of :code:`'Ch1', 'Ch2', 'Ch3', 'Ch4', 'Ch5', 'Ch6', 'Ch7', 'Ch8'`, while EEG channels are recording from a standard wavecap and should offer ['Fp1', 'Fpz', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8', 'FC5', 'FC1', 'FC2', 'FC6', 'M1', 'T7', 'C3', 'Cz', 'C4', 'T8', 'M2', 'CP5', 'CP1', 'CP2', 'CP6', 'P7', 'P3', 'Pz', 'P4', 'P8', 'POz', 'O1', 'O2', 'EOG', 'AF7', 'AF3', 'AF4', 'AF8', 'F5', 'F1', 'F2', 'F6', 'FC3', 'FCz', 'FC4', 'C5', 'C1', 'C2', 'C6', 'CP3', 'CP4', 'P5', 'P1', 'P2', 'P6', 'PO5', 'PO3', 'PO4', 'PO6', 'FT7', 'FT8', 'TP7', 'TP8', 'PO7', 'PO8', 'Oz'] all in reference to Cpz.


    returns
    -------
    Traces: List[TraceData]
        the TraceData for each event fitting to select_events in the file
    pre_in_samples:int
        how many samples before the trigger
    post_in_samples:int
        how many samples after the trigger
    sampling_rate: float
        the sampling rate of the trace
    """

    if not is_eegfile_valid(eeg_fname):
        raise ValueError(
            f"{eeg_fname} has not the correct file signature for a smartmove eeg file"
        )

    assert_equal_recording_day(eeg_fname, emg_fname)
    filedate = str(parse_recording_date(eeg_fname))

    eeg = cnt_file(eeg_fname)
    eeg_labels = [eeg.get_channel_info(i)[0] for i in range(eeg.get_channel_count())]

    emg = cnt_file(emg_fname)
    emg_labels = [emg.get_channel_info(i)[0] for i in range(emg.get_channel_count())]

    # the triggers are always recorded with EEG, so we need this Fs
    triggers = load_triggers(eeg_fname)
    eeg_fs = eeg.get_sample_frequency()

    if select_channel in eeg_labels:
        cnt = eeg
    elif select_channel in emg_labels:
        cnt = emg
    else:
        raise IndexError(f"Selected channel {select_channel} not found")

    origin = Path(cnt._fname).name
    subject = (Path(eeg_fname).stem.split("_")[0],)
    fs = cnt.get_sample_frequency()
    pre = int(pre_in_ms * fs / 1000)
    post = int(post_in_ms * fs / 1000)
    scale = fs / eeg_fs
    enames = []
    onsets = []
    tstamps = []

    for event, sample in triggers:
        if event in select_events:
            onset = int(sample * scale)
            onsets.append(onset)
            tstamps.append(sample / eeg_fs)
            enames.append(event)

    time_since_last_pulse = [inf] + [a - b for a, b in zip(tstamps[1:], tstamps[0:-1])]
    info = {
        "origin": origin,
        "event_samples": onsets,
        "event_times": tstamps,
        "event_names": enames,
        "samples_pre_event": pre,
        "samples_post_event": post,
        "samplingrate": fs,
        "subject": subject,
        "channel_labels": [select_channel],
        "time_since_last_pulse": time_since_last_pulse,
        "filedate": filedate,
    }
    return info


# -----------------------------------------------------------------------------


def prepare_annotations(
    docfile: FileName,
    eegfile: FileName,
    emgfile: FileName,
    channel: str,
    readout: str,
    pre_in_ms: float,
    post_in_ms: float,
) -> Annotations:
    """load a documentation.txt and cnt-files and distill annotations from them
    
    args
    ----
    docfile: FileName
        the documentation.txt with the target coordintes
    eegfile: FileName
        the :code:`.cnt`-file with the EEG data and triggers
    emgfile: FileName
        the :code:`.cnt`-file with the EMG data
    readout: str
        which readout to use (see :data:`~.VALID_READOUTS`)
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
    if readout not in VALID_READOUTS:
        raise NotImplementedError(f"{readout} is not implemented")

    # collect data
    info = load_ephys_file(
        eeg_fname=eegfile,
        emg_fname=emgfile,
        pre_in_ms=pre_in_ms,
        post_in_ms=post_in_ms,
        select_events=["0001"],
        select_channel=channel,
    )
    coords = load_documentation_txt(docfile)
    stimulation_intensity_mso = nan
    stimulation_intensity_didt = nan

    # trace fields
    traceattrs: List[MetaData] = []
    event_names = info["event_names"]
    event_samples = info["event_samples"]
    event_times = info["event_times"]
    time_since_last_pulse = info["time_since_last_pulse"]
    for idx, t in enumerate(event_samples):
        tattr = {
            "id": idx,
            "event_name": f"'{event_names[idx]}'",
            "event_sample": event_samples[idx],
            "event_time": event_times[idx],
            "xyz_coords": coords[idx],
            "time_since_last_pulse_in_s": time_since_last_pulse[idx],
            "stimulation_intensity_mso": stimulation_intensity_mso,
            "stimulation_intensity_didt": stimulation_intensity_didt,
            "reject": False,
            "comment": "",
            "examiner": "",
            "onset_shift": 0,
        }
        for key in SPECIFIC_TRACEKEYS[readout].keys():
            if key not in tattr.keys():
                tattr[key] = nan
        traceattrs.append(tattr)

    anno: Annotations = {
        "origin": info["origin"],
        "attrs": {
            "filedate": info["filedate"],
            "subject": info["subject"],
            "samplingrate": info["samplingrate"],
            "samples_pre_event": info["samples_pre_event"],
            "samples_post_event": info["samples_post_event"],
            "channel_labels": info["channel_labels"],
            "readout": readout,
            "global_comment": "",
            "history": "",
            "version": release,
        },
        "traces": traceattrs,
    }
    return anno


def cut_traces(cntfile: FileName, annotation: Annotations) -> List[TraceData]:
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
    pre = annotation["attrs"]["samples_pre_event"]
    post = annotation["attrs"]["samples_post_event"]
    cix = [cnt.get_channel_info(c)[0] for c in range(cnt.get_channel_count())].index(
        annotation["attrs"]["channel_labels"][0]
    )
    traces = []
    for attrs in annotation["traces"]:
        onset = attrs["event_sample"]
        trace = cnt.get_samples(fro=onset - pre, to=onset + post)
        trace = np.asanyarray(trace)[:, cix]
        traces.append(trace)
    return traces
