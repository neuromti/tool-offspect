import pytest
from offspect.cache.readout.converter import *
from offspect.api import CacheFile


@pytest.fixture
def attrs(cachefile0):
    yield CacheFile(cachefile0[0]).get_trace_attrs(0)


@pytest.fixture
def conv(attrs):
    mapper = dict()
    for key in attrs.keys():
        mapper[key] = pass_value
    c = Converter(**mapper)
    yield c


def test_converter_creation(conv, attrs):
    d = conv(**attrs)
    assert d == attrs


def test_converter_is_complete(conv, attrs):
    assert conv.is_complete(attrs)


def test_converter_is_not_complete(conv, attrs):
    key = list(attrs.keys())[0]
    attrs.pop(key)
    assert not conv.is_complete(attrs)


def test_converter_parses(attrs):
    mapper = dict()
    for key in attrs.keys():
        mapper[key] = parse
    c = Converter(**mapper)
    try:
        c(**attrs)
    except:
        assert False


def test_converter_addition(attrs):
    mapper0 = dict()
    mapper1 = dict()
    for ix, key in enumerate(attrs.keys()):
        if ix < len(attrs.keys()) // 2:
            mapper0[key] = pass_value
        else:
            mapper1[key] = pass_value
    a = Converter(**mapper0)
    b = Converter(**mapper1)
    d = a + b
    assert d(**attrs) == attrs

