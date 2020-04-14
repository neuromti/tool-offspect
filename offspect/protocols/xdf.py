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


# ------------------------------------------------------------------------------


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
    skip = False
    trigger_time = None
    try:
        while True:
            msg = decode_marker(next(marker))
            ts = next(tstamps)
            if msg == "Starte Hotspotsuche" or msg == "Starte Ruhemotorschwelle":
                skip = True
            if msg == "Starte freien Modus":
                skip = False
            if skip:
                continue
            if type(msg) is dict:
                if event_mark in msg.keys():
                    trigger_time = ts  # this is when we received a TriggerOut from
                if "amplitude" in msg.keys() and msg["amplitude"] != 0:
                    trigger_time = trigger_time or ts
                    pos = [msg[dim] for dim in ["x", "y", "z"]]
                    if not any(p == None for p in pos):
                        yield trigger_time
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
        print("Picking localite, overwriting any event_name argument")
        yield from yield_timestamps_localite(stream, event_mark="coil_0_didt")
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

