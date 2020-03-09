"""
Smartmove robotic
-----------------

These recordings come from the `smartmove robotic TMS <https://www.ant-neuro.com/products/smartmove>`_. This input format uses three files:

- :code:`.cnt` for EEG
- :code:`.cnt` for EMG
- :code:`.txt` for Coordinates

Data
****

EEG and EMG data is stored in the native file-format of the eego recording software. It can be loaded with `libeep <https://github.com/translationalneurosurgery/libeep>`_. During robotic TMS, the 64 EEG channels and the 8 EMG channels are stored in
separate :code:`.cnt` files.  

Coordinates
***********

The coordinates of the targets are stored in one or multiple :code:`targets_*.sav`-files in xml format. The filename of this save
file encodes experiment, subject pseudonym, date and hour, e.g.:
:code:`targets_<experiment>_<VvNn>_20190603_1624.sav`. These coordinates are the e.g. the grid of targets predefined before starting the mapping.

During the mapping procedure, the coordinates of the target positions, i.e. where the robot will be moved to, are saved in a :code:`documentation.txt`-file. Please note that these are the targets for the robotic movement, 
recorded, not the actual coordinates of stimulation. The actual coordinates at the time of stimulation do not appear to have been stored at all. 

Documentation of the syntax for these :code:`.txt` files will follow.

.. note::

   Load the :class:`TraceData` with :func:`~.load_ephys_file` and the :class:`Coords` with :func:`load_documentation_txt`.


Module Content
**************

"""

from offspect.types import FileName, Coords, TraceData
from pathlib import Path
from ast import literal_eval
from typing import List, Tuple
from datetime import datetime
import numpy as np
from os import environ

if not environ.get("READTHEDOCS", False):
    from libeep import cnt_file


def load_documentation_txt(fname: FileName) -> Coords:
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
            tmp = ", ".join(target[3].split(" "))
            xyz = literal_eval(f"[{tmp}]")
            target = []
            idx += 1
            coords[idx] = xyz[0:3]  # TODO unclear, discuss with Felix

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


def load_ephys_file(
    eeg_fname: FileName,
    emg_fname: FileName,
    pre_in_ms: float = 100,
    post_in_ms: float = 100,
    select_events: List[str] = ["0001"],
    select_channel: str = "Ch1",
) -> List[TraceData]:
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
    
    """

    if not is_eegfile_valid(eeg_fname):
        raise ValueError(
            f"{eeg_fname} has not the correct file signature for a smartmove eeg file"
        )

    eeg_day = parse_recording_date(eeg_fname)
    emg_day = parse_recording_date(emg_fname)
    assert eeg_day.year == emg_day.year
    assert eeg_day.month == emg_day.month
    assert eeg_day.day == emg_day.day
    triggers = load_triggers(eeg_fname)
    eeg = cnt_file(eeg_fname)
    emg = cnt_file(emg_fname)
    eeg_labels = [eeg.get_channel_info(i)[0] for i in range(eeg.get_channel_count())]

    # the triggers are always recorded with EEG, so we need this Fs
    eeg_fs = eeg.get_sample_frequency()

    emg_labels = [emg.get_channel_info(i)[0] for i in range(emg.get_channel_count())]
    if select_channel in eeg_labels:
        cnt = eeg
        cix = eeg_labels.index(select_channel)
    elif select_channel in emg_labels:
        cnt = emg
        cix = emg_labels.index(select_channel)
    else:
        raise IndexError(f"Selected channel {select_channel} not found")

    trace_fs = cnt.get_sample_frequency()
    pre = int(pre_in_ms * trace_fs / 1000)
    post = int(post_in_ms * trace_fs / 1000)
    traces = []
    for event, sample in triggers:
        if event in select_events:
            tstamp = int(sample * trace_fs / eeg_fs)
            # calculate the closest sample
            trace = np.atleast_2d(cnt.get_samples(tstamp - pre, tstamp + post))
            traces.append(trace[:, cix])
    return traces
