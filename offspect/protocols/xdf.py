from offspect.protocols.mat import get_coords_from_xml
from liesl.files.xdf.load import XDFStream
from typing import List, Any, Dict, Union
import json
import numpy as np
from math import nan


def decode_marker(mark: str) -> Any:
    try:
        msg = json.loads(mark[0])
        return msg
    except json.JSONDecodeError:
        return mark[0]


def pick_stream_with_channel(channel: str, streams: Dict[str, XDFStream]) -> XDFStream:
    chans: List[str] = []
    datastream = None
    for stream in streams.values():
        if stream.channel_labels is not None:
            chans.extend(stream.channel_labels)
            if channel in stream.channel_labels:
                datastream = stream

    if datastream is None:
        raise IndexError(
            f"Could not find the channel {channel} in any stream in the file. Available are: {chans}"
        )
    return datastream


def find_closest_samples(stream: XDFStream, tstamps: List[float]) -> List[int]:
    event_samples = []
    for ts in tstamps:
        idx = int(np.argmin(np.abs(stream.time_stamps - ts)))
        event_samples.append(idx)
    return event_samples


def find_closest(ts: float, timestamps: List[float], relative: str = "closest"):
    idx = find_closest_idx(ts, timestamps, relative)
    return timestamps[idx]


def find_closest_idx(ts: float, timestamps: List[float], relative: str = "closest"):
    if relative == "earlier":  # closest in time, but comment was earlier
        rt = [t - ts for t in timestamps if t <= ts]
    elif relative == "later":  # closest in time, but comment was later
        rt = [t - ts for t in timestamps if t >= ts]
    else:  # closest in time
        rt = [t - ts for t in timestamps]
    idx = np.argmin(np.abs(rt))
    return idx


def tkeo(a):
    """
	Calculates the TKEO of a given recording by using 2 samples.
	See Li et al., 2007
	Arguments:
	a 			--- 1D numpy array.
	Returns:
	1D numpy array containing the tkeo per sample
	"""

    # Create two temporary arrays of equal length, shifted 1 sample to the right
    # and left and squared:
    i = a[1:-1] * a[1:-1]
    j = a[2:] * a[:-2]

    # Calculate the difference between the two temporary arrays:
    aTkeo = i - j

    return aTkeo


def correct_tkeo(bvr, time_stamps: List[float]) -> List[float]:
    eeg_labels = [
        "Fp1",
        "Fp2",
        "F3",
        "F4",
        "C3",
        "C4",
        "P3",
        "P4",
        "O1",
        "O2",
        "F7",
        "F8",
        "T7",
        "T8",
        "P7",
        "P8",
        "Fz",
        "Cz",
        "Pz",
        "Iz",
        "FC1",
        "FC2",
        "CP1",
        "CP2",
        "FC5",
        "FC6",
        "CP5",
        "CP6",
        "FT9",
        "FT10",
        "TP9",
        "TP10",
        "F1",
        "F2",
        "C1",
        "C2",
        "P1",
        "P2",
        "AF3",
        "AF4",
        "FC3",
        "FC4",
        "CP3",
        "CP4",
        "PO3",
        "PO4",
        "F5",
        "F6",
        "C5",
        "C6",
        "P5",
        "P6",
        "AF7",
        "AF8",
        "FT7",
        "FT8",
        "TP7",
        "TP8",
        "PO7",
        "PO8",
        "Fpz",
        "CPz",
        "POz",
        "Oz",
    ]
    pick = [label in eeg_labels for label in bvr.channel_labels]
    artifact = tkeo(np.std(np.compress(pick, bvr.time_series, axis=1), axis=1))

    new_ts = []
    for ts in time_stamps:
        onset = find_closest_idx(ts, bvr.time_stamps)
        hood = artifact[onset - 50 : onset + 50]
        new_ts.append(bvr.time_stamps[onset + np.argmax(hood) - 50])
    return new_ts


# -----------------------------------------------------------------------------


def yield_timestamps_brainvision_rda_marker(stream, event_mark="S  2"):
    "go through all triggers and  yield the timestamps of the events"
    marker = iter(stream.time_series)
    tstamps = iter(stream.time_stamps)
    try:
        while True:
            msg = decode_marker(next(marker))
            ts = next(tstamps)
            if msg == event_mark:
                yield ts

    except StopIteration:
        return


def yield_timestamps_spongebob(stream, event_mark=1):
    data = iter(stream.time_series[:, 11])
    tstamps = iter(stream.time_stamps)
    try:
        while True:
            msg = int(next(data))
            ts = next(tstamps)
            if msg == event_mark:
                yield ts

    except StopIteration:
        return


def yield_timestamps_localite(stream, event_mark="coil_0_didt"):
    marker = iter(stream.time_series)
    tstamps = iter(stream.time_stamps)
    trigger_time = None
    try:
        while True:
            msg = decode_marker(next(marker))
            ts = next(tstamps)
            if (
                msg == "Starte Hotspotsuche"
                or msg == "Starte Ruhemotorschwelle"
                or msg == "Starte freien Modus"
            ):
                continue
            if type(msg) is dict:
                if event_mark in msg.keys():
                    # this is the timestamp when we received a TriggerOut confirmation from the Localite Server
                    trigger_time = ts
                if "amplitude" in msg.keys() and msg["amplitude"] != 0:
                    # greedy evaluation makes sure i either get the first,
                    # and  the second only if the first is falseish or None
                    # so it is either the timestamp from event_mark, or the
                    # one were we received no confirmation
                    trigger_time = trigger_time or ts
                    pos = [msg[dim] for dim in ["x", "y", "z"]]
                    # if not any(p == None for p in pos):
                    yield trigger_time
                    # else:
                    #    print("Event is missing coordinates. Skipping")
                    trigger_time = None

    except StopIteration:
        return


def yield_timestamps(stream: XDFStream, event_mark: Union[str, int]):
    "go through all triggers and  yield the timestamps of the events"
    if stream.name == "BrainVision RDA Markers":
        yield from yield_timestamps_brainvision_rda_marker(stream, event_mark)
    elif stream.name == "Spongebob-Data":
        yield from yield_timestamps_spongebob(stream, event_mark)
    elif stream.name == "localite_marker" or stream.name == "localite_flow":
        if event_mark != "coil_0_didt":
            print(
                "Picking localite, overwriting any event_name argument and using 'coil_0_didt'"
            )
            event_mark = "coil_0_didt"

        yield from yield_timestamps_localite(stream, event_mark)
    else:
        raise NotImplementedError(f"Parsing {stream.name} is not implemented")


def yield_comments(
    stream: XDFStream,
    time_stamps: List[float],
    identifier: str = "stimulus_idx",
    relative="earlier",
):
    comments: List[str] = []
    ct: List[float] = []
    for t, m in zip(stream.time_stamps, stream.time_series):
        if identifier in m[0]:
            comments.append(m)
            ct.append(t)
    for ts in time_stamps:
        if len(ct) == 0:
            yield ""
            continue
        if relative == "earlier":  # closest in time, but comment was earlier
            _ct = [t - ts for t in ct if t <= ts]
        elif relative == "later":  # closest in time, but comment was later
            _ct = [t - ts for t in ct if t >= ts]
        else:  # closest in time
            _ct = [t - ts for t in ct]
        idx = np.argmin(np.abs(_ct))
        # we pop, therefore no comment can be returned twice
        ct.pop(idx)
        yield comments.pop(idx)[0]


def yield_loc_coords(
    stream: XDFStream, time_stamps: List[float], relative: str = "later"
):
    coords = []
    ct: List[float] = []
    for t, m in zip(stream.time_stamps, stream.time_series):
        msg = decode_marker(m)
        if type(msg) is dict:
            if "amplitude" in msg.keys() and msg["amplitude"] != 0:
                pos = [msg[dim] for dim in ["x", "y", "z"]]
                coords.append(pos)
                ct.append(t)
    print(f"Found {len(coords)} coordinates for {len(time_stamps)} events", end="")
    if len(ct) < len(time_stamps):
        print(". Filling up missing information with nan")
    else:
        print()
    for ts in time_stamps:
        if relative == "earlier":  # closest in time, but comment was earlier
            _ct = [t - ts for t in ct if t <= ts]
        elif relative == "later":  # closest in time, but comment was later
            _ct = [t - ts for t in ct if t >= ts]
        else:  # closest in time
            _ct = [t - ts for t in ct]
        idx = np.argmin(np.abs(_ct))
        # we pop, therefore no coordinate can be returned twice
        ct.pop(idx)
        yield coords.pop(idx)


def yield_loc_mso(stream: XDFStream, time_stamps: List[float], relative: str = "later"):
    mso = []
    ct: List[float] = []
    for t, m in zip(stream.time_stamps, stream.time_series):
        msg = decode_marker(m)
        if type(msg) is dict:
            if "amplitude" in msg.keys() and msg["amplitude"] != 0:
                mso.append(msg["amplitude"])
                ct.append(t)

    print(f"Found {len(ct)} mso comments for {len(time_stamps)} events", end="")
    if len(ct) < len(time_stamps):
        print(". Filling up missing information with nan")
    else:
        print()
    for ts in time_stamps:
        if relative == "earlier":  # closest in time, but comment was earlier
            _ct = [t - ts for t in ct if t <= ts]
        elif relative == "later":  # closest in time, but comment was later
            _ct = [t - ts for t in ct if t >= ts]
        else:  # closest in time
            _ct = [t - ts for t in ct]
        idx = np.argmin(np.abs(_ct))
        # we pop, therefore no coordinate can be returned twice
        ct.pop(idx)
        yield mso.pop(idx)


def yield_loc_didt(
    stream: XDFStream,
    time_stamps: List[float],
    event_mark: str = "coil_0_didt",
    relative: str = "closest",
):
    didt = []
    ct: List[float] = []
    for t, m in zip(stream.time_stamps, stream.time_series):
        msg = decode_marker(m)
        if type(msg) is dict:
            if event_mark in msg.keys():
                didt.append(msg[event_mark])
                ct.append(t)
    print(f"Found {len(ct)} didt comments for {len(time_stamps)} events", end="")
    if len(ct) < len(time_stamps):
        print(". Filling up missing information with nan")
    else:
        print()
    for ts in time_stamps:
        if len(ct) == 0:
            yield nan
            continue
        if relative == "earlier":  # closest in time, but comment was earlier
            _ct = [t - ts for t in ct if t <= ts]
        elif relative == "later":  # closest in time, but comment was later
            _ct = [t - ts for t in ct if t >= ts]
        else:  # closest in time
            _ct = [t - ts for t in ct]
        idx = np.argmin(np.abs(_ct))
        # we pop, therefore no coordinate can be returned twice
        ct.pop(idx)
        yield didt.pop(idx)


def list_nan_coords(count: int):
    return [[nan, nan, nan] for i in range(count)]


def list_nan(count: int):
    return [nan for i in range(count)]


def has_localite(stream_names: List[str]) -> bool:
    localite_names = ["localite_flow", "localite_marker"]
    for l in localite_names:
        if l in stream_names:
            return True
    return False


def has_spongebob(stream_names: List[str]) -> bool:
    spongebob_name = "Spongebob-Data"
    return spongebob_name in stream_names
