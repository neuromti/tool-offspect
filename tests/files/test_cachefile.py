import pytest
from offspect.cache import file as hdf
from offspect.cache.file import recover_parts, check_valid_suffix


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


def test_check_valid_suffix():
    with pytest.raises(ValueError):
        check_valid_suffix("test.wrong")
    assert check_valid_suffix("test.hdf5") == None


def test_cachefile_recover(cachefile0):
    cachefile, settings = cachefile0
    cf = hdf.CacheFile(cachefile)
    events, traces = recover_parts(cf)
    assert len(events) == 1  # comes only from a single source file
    assert len(traces) == 1  # comes only from a single source file

    # lets reduce indexing for later comparions
    events = events[0]
    traces = traces[0]
    # assert recovery was succesfull for the event info
    assert events["origin"] == settings["origin"]
    for key in events["attrs"].keys():
        assert events["attrs"][key] == settings["attrs"][key]
    for rec, orig in zip(events["traces"], settings["traces"]):
        for key in rec.keys():
            assert rec[key] == orig[key]
    # assert recovery was succesfull for the traced data
    assert len(traces) == len(settings["traces"])
