import pytest
from offspect.api import CacheFile
from offspect.cache.readout.always import *


@pytest.fixture
def valid_attrs(cachefile0):
    yield CacheFile(cachefile0[0]).get_trace_attrs(0)


def test_check_required_keys_exist(valid_attrs):
    check_required_keys_exist(**valid_attrs)


def test_check_required_keys_exist_fails(valid_attrs):
    del valid_attrs["history"]
    with pytest.raises(KeyError):
        check_required_keys_exist(**valid_attrs)
