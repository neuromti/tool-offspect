import pytest
from offspect.input.tms.smartmove import *
from tempfile import mkdtemp
from pathlib import Path


@pytest.fixture
def doctxt():
    f = Path(__file__).parent.parent.parent / "mock" / "documentation.txt"
    yield str(f)


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


eeg_fname = "tests/mock/VvNn_VvNn_2000-12-31_23-59-59.cnt"

emg_fname = "tests/mock/VvNn 2000-12-31_23-59-59.cnt"


@pytest.mark.iosmartmove
@pytest.mark.skipif(not Path(eeg_fname).exists(), reason="No files found")
def test_load_ephys_file():
    traces = load_ephys_file(eeg_fname, emg_fname)

