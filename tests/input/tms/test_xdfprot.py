import pytest
from offspect.input.tms.xdfprot import *
from pathlib import Path


def test_convert_xdf(get_xdffile):
    xdffile = get_xdffile("stroke_map.xdf")
    annotation = prepare_annotations(
        xdffile=xdffile,
        channel="EDC_L",
        # readout="tms_cmep",
        readout="contralateral_mep",
        pre_in_ms=100,
        post_in_ms=100,
        event_names="coil_0_didt",
        event_stream="localite_marker",
    )
    print(annotation)
    traces = cut_traces(xdffile, annotation)
    print(len(traces))
    assert len(traces) == 20
