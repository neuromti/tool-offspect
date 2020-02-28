import pytest
from offspect.cache import file as hdf


def test_cache_tmp_attributes(cachefile):
    cachefile, settings = cachefile
    assert cachefile.exists()
    cf = hdf.CacheFile(cachefile)

    assert len(settings) == len(cf.origins)
    assert settings[0]["origin"] == cf.traces[0][0]["origin"]
    exp_trace_count = sum([len(yml["traces"]) for yml in settings])
    assert exp_trace_count == len(cf.traces)
    print(cf.traces)
