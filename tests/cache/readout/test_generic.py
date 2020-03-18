import pytest
from offspect.api import CacheFile
from offspect.cache.readout.generic import *


@pytest.fixture
def valid_attrs(cachefile0):
    yield CacheFile(cachefile0[0]).get_trace_attrs(0)


def test_keys_exist(valid_attrs):
    keys_exist(**valid_attrs)


def test_keys_exist_fails(valid_attrs):
    del valid_attrs["history"]
    with pytest.raises(KeyError):
        keys_exist(**valid_attrs)
