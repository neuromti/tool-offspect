import pytest
import os
from offspect.input.tms import xdfprot
from pyxdf import load_xdf

@pytest.fixture
def XDFMarkerstream():
    streams, fileheader = load_xdf(xdffile)
    streams_as_dict = {}
    for ix, stream in enumerate(streams):
        streamname = stream['info']['name'][0]
        streams_as_dict[streamname] = stream
    return streams_as_dict

xdffile = "/home/juli/acute_study/recordings/NoDi/IMONAS-acute-study-intervention_R001.xdfx"
xdffile_found = os.path.isfile(xdffile)

@pytest.mark.skipif(xdffile_found == False, reason="Could not find the xdf test files")
@pytest.fixture
def xdf_streams():
    streams, fileheader = load_xdf(xdffile)
    streams_as_dict = {}
    for ix, stream in enumerate(streams):
        streamname = stream['info']['name'][0]
        streams_as_dict[streamname] = stream
    return streams_as_dict

@pytest.mark.skipif(xdffile_found == False, reason="Could not find the xdf test files")
@pytest.fixture
def spongebob_stream(xdf_streams):
    return xdf_streams['Spongebob-Data']

@pytest.mark.skipif(xdffile_found == False, reason="Could not find the xdf test files")
def test_yield_target_values(spongebob_stream):
    target_value_list = list(xdfprot.yield_target_values(spongebob_stream, 1, 11))
    assert(len(target_value_list) > 1900)

def test_valid_info_for_trigger():
    info_tsp_0 = 4
    trigger_tsp_0 = 5
    info_tsp_1 = 205870.74691046
    trigger_tsp_1 = 205874.1
    info_tsp_2 = 5
    trigger_tsp_2 = 4

    assert(xdfprot.valid_info_for_trigger(info_tsp_0, trigger_tsp_0) == True)
    assert(xdfprot.valid_info_for_trigger(info_tsp_1, trigger_tsp_1) == True)
    assert(xdfprot.valid_info_for_trigger(info_tsp_2, trigger_tsp_2) == False)

def test_find_trigger_info(XDFMarkerStream):
    expected_trigger_info_1 = ['{"reaction_time": "199"}']
    trigger_info_1 = xdfprot.find_trigger_info(XDFMarkerStream, 205875.1)
    assert (expected_trigger_info_1 == trigger_info_1)

    expected_trigger_info_2 = ['{"stimulus_idx": "477", "stim_type": "PVT", "freq": "8", "phase": "225"}']
    trigger_info_2 = xdfprot.find_trigger_info(XDFMarkerStream, 205878)
    assert (expected_trigger_info_2 == trigger_info_2)
    
    expected_trigger_info_3 = None
    trigger_info_3 = xdfprot.find_trigger_info(XDFMarkerStream, 3)
    assert (expected_trigger_info_3 == trigger_info_3)