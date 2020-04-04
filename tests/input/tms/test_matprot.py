import pkg_resources
import pytest
from pathlib import Path
from offspect.input.tms.matprotconv import prepare_annotations, cut_traces
from offspect.api import populate, CacheFile
from matprot.convert.traces import is_matlab_installed


@pytest.mark.skipif(is_matlab_installed() == False, reason="Matlab is not installed")
def test_matprot(tmp_path, get_matprot):
    xmlfile, matfile = get_matprot
    annotation = prepare_annotations(
        xmlfile,
        matfile,
        channel_of_interest="EDC_L",
        pre_in_ms=100,
        post_in_ms=100,
        readout="cmep",
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
