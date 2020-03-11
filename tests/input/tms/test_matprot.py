import pkg_resources
import pytest
from pathlib import Path
from offspect.input.tms.matprotconv import prepare_annotations, cut_traces
from offspect.api import populate, CacheFile


def test_matprot(tmp_path):
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
