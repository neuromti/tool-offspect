import pkg_resources
import pytest
from pathlib import Path
from offspect.input.tms.matprotconv import prepare_annotations, cut_traces
from offspect.api import populate, CacheFile
from matprot.convert.traces import is_matlab_installed

try:
    matfile = list(
        (Path(pkg_resources.resource_filename("matprot", "")).parent / "tests").glob(
            "*.mat"
        )
    )[0]

    xmlfile = list(
        (Path(pkg_resources.resource_filename("matprot", "")).parent / "tests").glob(
            "*.xml"
        )
    )[0]
    found = True
except IndexError:
    found = False


@pytest.mark.skipif(found == False, reason="Could not find the test files")
@pytest.mark.skipif(is_matlab_installed() == False, reason="Matlab is not installed")
def test_matprot(tmp_path):

    annotation = prepare_annotations(
        xmlfile,
        matfile,
        channel="EDC_L",
        pre_in_ms=100,
        post_in_ms=100,
        readout="contralateral_mep",
    )

    traces = cut_traces(matfile, annotation)

    d = tmp_path / "matprot"
    d.mkdir(exist_ok=True)
    tf = d / "test.hdf5"

    populate(tf, annotations=[annotation], traceslist=[traces])
    cf = CacheFile(tf)
    assert cf.origins[0] == matfile.name
