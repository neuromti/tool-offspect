import pytest
from offspect.input.tms.cmep.xdf import *
from pathlib import Path
from subprocess import Popen, PIPE


@pytest.mark.parametrize("recording", ["stroke_map.xdf"])
def test_convert_xdf(get_xdffile, recording):
    xdffile = get_xdffile(recording)
    annotation = prepare_annotations(
        xdffile=xdffile,
        channel="EDC_L",
        pre_in_ms=100,
        post_in_ms=100,
        event_name="coil_0_didt",
        event_stream="localite_marker",
    )
    traces = cut_traces(xdffile, annotation)
    assert len(traces) == 20


# @pytest.mark.parametrize(
#    "recording", ["acute_tms.xdf", "acute_nmes.xdf", "stroke_map.xdf"]
# )
@pytest.mark.parametrize("recording", ["stroke_map.xdf"])
def test_xdf_cli(tmp_path, get_xdffile, recording):
    xdffile = get_xdffile(recording)
    d = tmp_path / "xdf"
    d.mkdir(exist_ok=True)
    tf = d / Path(recording).with_suffix(".hdf5")
    p = Popen(
        [
            "offspect",
            "tms",
            "-f",
            str(xdffile),
            "-r",
            "cmep",
            "-pp",
            "100",
            "100",
            "-t",
            str(tf),
            "-c",
            "EDC_L",
        ],
        stdout=PIPE,
        stderr=PIPE,
    )
    time.sleep(1)
    o, e = p.communicate()
    print(o, e)
    assert tf.name in o.decode()
    assert e == b""
    tf.unlink()
