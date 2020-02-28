import pytest
from offspect.cache import file as hdf
from offspect.cache.file import recover_parts


def test_cachefile_creation(cachefile0, cachefile1):
    for cache in [cachefile0, cachefile1]:
        cachefile, settings = cache
        assert cachefile.exists()
        cf = hdf.CacheFile(cachefile)
        assert len(cf.origins) == 1
        assert settings["origin"] == cf.traces[0][0]["origin"]
        # exp_trace_count = sum([len(settings["traces"]) for yml in settings])
        exp_trace_count = len(settings["traces"])
        assert exp_trace_count == len(cf.traces)


def test_cachefile_recover(cachefile0):
    cachefile, settings = cachefile0
    cf = hdf.CacheFile(cachefile)
    events, traces = recover_parts(cf)
    assert events["origin"] == settings["origin"]
    for key in events["attrs"].keys():
        assert events["attrs"][key] == settings["attrs"][key]
    for rec, orig in zip(events["traces"], settings["traces"]):
        for key in rec.keys():
            assert rec[key] == orig[key]
    assert len(traces) == len(settings["traces"])
