import pytest
from offspect.input.tms.cmep.smartmove import *
from tempfile import mkdtemp
from pathlib import Path
import libeep


@pytest.fixture
def doctxt():
    f = Path(__file__).parent.parent.parent.parent / "mock" / "documentation.txt"
    yield str(f)


@pytest.fixture()
def emg_cnt(tmp_path):
    d = tmp_path / "tests"
    d.mkdir(exist_ok=True)
    fname = Path(d) / "VvNn 2000-12-31_23-59-59.cnt"
    if fname.exists():
        fname.unlink()
    fname = str(fname)
    rate = 1024
    channel_count = 8
    channels = [(f"Ch{i}", "None", "uV") for i in range(1, channel_count + 1, 1)]
    c = libeep.cnt_out(fname, rate, channels)
    samples = np.repeat(np.arange(0, 5000), 8).flatten().tolist()
    c.add_samples(samples)
    c.close()
    yield fname


@pytest.fixture()
def eeg_cnt(tmp_path):
    d = tmp_path / "tests"
    d.mkdir(exist_ok=True)
    fname = Path(d) / "VvNn_VvNn_2000-12-31_23-59-59.cnt"
    if fname.exists():
        fname.unlink()
    fname = str(fname)
    rate = 1000
    channel_count = 64
    channels = [(f"EEG{i}", "None", "uV") for i in range(1, channel_count + 1, 1)]
    c = libeep.cnt_out(fname, rate, channels)
    samples = np.repeat(np.arange(0, 5000), 8).flatten().tolist()
    c.add_samples(samples)
    tstamps = (1000, 2048)
    for t in tstamps:
        c.add_trigger(t, "0001")
    c.close()
    yield fname, tstamps


def test_load_document_txt_raises(doctxt, tmpdir):
    erroneous = tmpdir.mkdir("smartmove") / "documentation.txt"
    with Path(doctxt).open("r") as f:
        lines = f.readlines()

    lines[14] = "off"  # subject is different
    with erroneous.open("w") as f:
        f.write("".join(lines))
    with pytest.raises(ValueError):
        load_documentation_txt(str(erroneous))

    lines[13] = "off"  # experiment is different
    with erroneous.open("w") as f:
        f.write("".join(lines))
    with pytest.raises(ValueError):
        load_documentation_txt(str(erroneous))

    lines[8] = "3"  # index is wrong
    with erroneous.open("w") as f:
        f.write("".join(lines))
    with pytest.raises(ValueError):
        load_documentation_txt(str(erroneous))


def test_load_document_txt(doctxt):
    with pytest.raises(ValueError):
        load_documentation_txt("invalid.txt")
    load_documentation_txt(doctxt)


def test_is_eegfile_valid():
    assert is_eegfile_valid("VvNn_VvNn_YYYY-MM-DD_HH-MM-SS.cnt")
    assert not is_eegfile_valid("VvNn_VvNn_YYYY-MM-DD_HH-MM-SS.off")
    assert not is_eegfile_valid("VvNn_ElSe_YYYY-MM-DD_HH-MM-SS.cnt")
    assert not is_eegfile_valid("VN_VN_YYYY-MM-DD_HH-MM-SS.cnt")
    assert not is_eegfile_valid("vvNn_vvNn_YYYY-MM-DD_HH-MM-SS.cnt")
    assert not is_eegfile_valid("VVNn_VVNn_YYYY-MM-DD_HH-MM-SS.cnt")


def test_parse_recording_date():
    with pytest.raises(Exception):
        parse_recording_date("VVNn_VVNn_YYYY-MM-DD_HH-MM-SS.cnt")
    date = parse_recording_date("VVNn_VVNn_1970-01-02_00-00-01.cnt")
    assert date.year == 1970
    assert date.month == 1
    assert date.day == 2
    assert date.hour == 0
    assert date.minute == 0
    assert date.second == 1


def test_load_ephys_file(eeg_cnt, emg_cnt):
    eeg_cnt, onsets = eeg_cnt
    info = load_ephys_file(eeg_cnt, emg_cnt)
    assert len(info["event_samples"]) == 2
    assert info["event_samples"] == [int(o * 1024 / 1000) for o in onsets]


def test_convert_smartmove(eeg_cnt, emg_cnt, doctxt):
    eeg_cnt, onsets = eeg_cnt
    cntfiles = [eeg_cnt, emg_cnt]
    anno = prepare_annotations(doctxt, cntfiles, "Ch1", 100, 100)
    assert anno["origin"] == Path(emg_cnt).name
    assert len(anno["traces"]) == 2
    assert [a["event_time"] for a in anno["traces"]] == [str(o / 1000) for o in onsets]

    traces = cut_traces(emg_cnt, anno)
    for (trace, t) in zip(traces, onsets):
        # should be 100ms before and after -> 102 samples
        assert trace.shape == (204,)
        # because data is 0 -> N, the center value should be the resampled original tstamp
        assert trace[102] == float(int(t * 1024 / 1000))
