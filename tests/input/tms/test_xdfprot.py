import pytest
from offspect.input.tms import xdfprot
from pyxdf import load_xdf

try:
    xdffile = "/home/juli/acute_study/recordings/NoDi/IMONAS-acute-study-intervention_R001.xdf"
    xdffile_found = True
except IndexError:
    xdffile_found = False

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
