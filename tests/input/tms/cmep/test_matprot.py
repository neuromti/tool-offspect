import pkg_resources
import pytest
from pathlib import Path
from offspect.input.tms.cmep.mat import prepare_annotations, cut_traces
from offspect.api import populate, CacheFile
from matprot.convert.traces import is_matlab_installed
from subprocess import Popen, PIPE
import time


@pytest.mark.skipif(is_matlab_installed() == False, reason="Matlab is not installed")
def test_matprot(tmp_path, get_matprot):
    xmlfile, matfile = get_matprot
    annotation = prepare_annotations(
        xmlfile, matfile, channel_of_interest="EDC_L", pre_in_ms=100, post_in_ms=100,
    )
    print(annotation)
    traces = cut_traces(matfile, annotation)

    d = tmp_path / "matprot"
    d.mkdir(exist_ok=True)
    tf = d / "test.hdf5"

    populate(tf, annotations=[annotation], traceslist=[traces])
    cf = CacheFile(tf)
    assert cf.origins[0] == Path(matfile).name
    assert len(cf) == 2


@pytest.mark.skipif(is_matlab_installed() == False, reason="Matlab is not installed")
def test_matprot_cli(tmp_path, get_matprot):
    xmlfile, matfile = get_matprot
    d = tmp_path / "matprot"
    d.mkdir(exist_ok=True)
    tf = d / "test.hdf5"

    p = Popen(
        [
            "offspect",
            "tms",
            "-f",
            str(xmlfile),
            str(matfile),
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
    assert "test.hdf5" in o.decode()
    assert e == b""
