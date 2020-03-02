import pytest
from offspect.cache.check import *


def test_check_trace_attributes_are_valid(cachefile0):
    cf, annotations = cachefile0
    readout = annotations["attrs"]["readout"]
    assert readout in VALID_READOUTS
    for traceattrs in annotations["traces"]:
        assert check_trace_attributes(readout, traceattrs) is None


def test_check_trace_attributes_invalid_readout(cachefile0):
    cf, annotations = cachefile0
    readout = "invalid_readout"
    assert readout not in VALID_READOUTS
    with pytest.raises(NotImplementedError):
        for traceattrs in annotations["traces"]:
            assert check_trace_attributes(readout, traceattrs) is None


def test_check_trace_attributes_key_missing(cachefile0):
    cf, annotations = cachefile0
    del annotations["traces"][0]["pos_peak_latency_ms"]
    readout = annotations["attrs"]["readout"]
    assert readout in VALID_READOUTS
    with pytest.raises(KeyError):
        for traceattrs in annotations["traces"]:
            assert check_trace_attributes(readout, traceattrs) is None


def test_check_trace_attributes_wrong_type(cachefile0):
    cf, annotations = cachefile0
    annotations["traces"][0]["xyz_coords"] = ""
    readout = annotations["attrs"]["readout"]
    assert readout in VALID_READOUTS
    with pytest.raises(ValueError):
        for traceattrs in annotations["traces"]:
            assert check_trace_attributes(readout, traceattrs) is None


@pytest.mark.parametrize("x", [0.0, -1.0, 1.0, None, ""])
def test_isnotint(x):
    assert not isint(x)


@pytest.mark.parametrize("x", [0, -1, 1])
def test_isint(x):
    assert isint(x)


@pytest.mark.parametrize("x", [0.0, -1.0, 1.0, 0.1])
def test_isfloat(x):
    assert isfloat(x)


@pytest.mark.parametrize("x", [0, -1, 1, None, ""])
def test_isnotfloat(x):
    assert not isfloat(x)


@pytest.mark.parametrize("x", [0, -1, 1, 0.1])
def test_isnumeric(x):
    assert isnumeric(x)


def test_iscoords():
    assert iscoords([0, 1, 1.2])  # in or float


def test_isnotcoords():
    assert not iscoords(["", 1, 1.2])  # not numeric
    assert not iscoords([None, 1, 1.2])  # not numeric
    assert not iscoords([1, 1.2])  # not xyz, i.e. not 3 entries
    assert not iscoords((0, 1, 1.2))  #  not a list


def test_isTsince():
    assert isTsince(0.001)
    assert isTsince(912321451)
    assert isTsince("")  # can also be left empty, because first pulse
    assert isTsince(None)  # can also be left empty, because first pulse


def test_isnotTsince():
    assert not isTsince(0)
    assert not isTsince(-1)

