import pytest
from offspect.cache.file import *
import tempfile
from pathlib import Path
import datetime


def test_cachefile_creation(cachefile0, cachefile1):
    for cache in [cachefile0, cachefile1]:
        cachefile, settings = cache
        assert cachefile.exists()
        cf = CacheFile(cachefile)
        assert len(cf.origins) == 1
        assert settings["origin"] == recover_annotations(cf)[0]["origin"]
        # exp_trace_count = sum([len(settings["traces"]) for yml in settings])
        exp_trace_count = len(settings["traces"])
        assert exp_trace_count == len(cf)


def test_cachefile_doesnotexist():
    with pytest.raises(FileNotFoundError):
        CacheFile("doesnotexist.hdf5")


def test_check_valid_suffix():
    with pytest.raises(ValueError):
        check_valid_suffix("test.wrong")
    assert check_valid_suffix("test.hdf5") == None


def test_cachefile_recover(cachefile0):
    cachefile, settings = cachefile0
    cf = CacheFile(cachefile)
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


def test_print_cachefile(cachefile0):
    "test whether the printout from cachefile contains info about origin file, and the original attributes"
    cf, a = cachefile0
    s = str(CacheFile(cf))
    assert a["origin"] in s
    for k, v in a["attrs"].items():
        assert str(k) in s
        assert str(v) in s


def test_merge_in_order(cachefile0, cachefile1):
    """test whether merge succeeds sucessfully if the two sources are consistent with each other"""
    cf0, a0 = cachefile0
    cf1, a1 = cachefile1
    with tempfile.NamedTemporaryFile(suffix=".hdf5", mode="wb") as tf:
        sources = [cf0, cf1]
        merge(to=tf.name, sources=sources)
        cf = CacheFile(tf.name)
        a = recover_annotations(cf)
        assert len(a) == 2
        assert a0 == a[0]
        assert a1 == a[1]
        assert len(cf) == 4


def test_merge_inconsistent_origins(cachefile0):
    "test that merge raises an exception if the sourcesfiles are equal"
    cf0, a0 = cachefile0
    with tempfile.NamedTemporaryFile(suffix=".hdf5", mode="wb", delete=False) as tf:
        sources = [cf0, cf0]
        with pytest.raises(Exception):
            merge(to=tf.name, sources=sources)
        assert Path(tf.name).exists() == False


def test_merge_inconsistent_attrs(cachefile0, cachefile0inconsistent):
    "test that merge raises an exception if the sourcesfiles are equal"
    cf0, a0 = cachefile0
    cf1, a1 = cachefile0inconsistent
    with tempfile.NamedTemporaryFile(suffix=".hdf5", mode="wb", delete=False) as tf:
        sources = [cf0, cf1]
        with pytest.raises(Exception):
            merge(to=tf.name, sources=sources)
        assert Path(tf.name).exists() == False


def test_update_trace_attributes(cachefile0):
    cf = CacheFile(cachefile0[0])
    attrs = read_trace(cf, what="attrs", idx=0)
    now = str(datetime.datetime.now())
    attrs["comment"] = now
    update_trace_attributes(attrs)
    new_attrs = read_trace(cf, what="attrs", idx=0)
    assert new_attrs["comment"] == now


def test_read_index_tracedata(cachefile0):
    cf = CacheFile(cachefile0[0])
    for i in range(len(cf)):
        data = read_trace(cf, idx=i, what="data")
        assert type(data) == ndarray
        assert data[0:50].mean() == 0.0  # baseline model, no signal
        assert data[50:150].mean() != 0.0  # we modeled a signal


def test_read_index_raises(cachefile0):
    cf = CacheFile(cachefile0[0])
    with pytest.raises(NotImplementedError):
        data = read_trace(cf, idx=0, what="notimplemented")


def test_read_index_errors(cachefile0):
    cf = CacheFile(cachefile0[0])
    # we can iterate across all traces
    for i in range(len(cf)):
        attrs = read_trace(cf, i)
        assert attrs["cache_file_index"] == str(i)
        assert attrs["cache_file"] == str(cf.fname)

    with pytest.raises(ValueError):
        read_trace(cf, 0.1)

    with pytest.raises(IndexError):
        read_trace(cf, -1)

    with pytest.raises(IndexError):
        read_trace(cf, len(cf))


def test_update_index_errors(cachefile0):
    cf = CacheFile(cachefile0[0])
    attrs = read_trace(cf, 0)  # need this for overwriting

    with pytest.raises(ValueError):
        attrs["cache_file_index"] = 0.1
        update_trace_attributes(attrs)

    with pytest.raises(Exception):
        attrs["cache_file_index"] = -1
        update_trace_attributes(attrs)

    with pytest.raises(IndexError):
        attrs["cache_file_index"] = str(len(cf))
        update_trace_attributes(attrs)


def test_cachefile_len(cachefile0):
    fname, default_attrs = cachefile0
    cf = CacheFile(fname)
    assert len(cf) == 2


def test_cachefile_getter_setter(cachefile0):
    cf = CacheFile(cachefile0[0])
    data = cf.get_trace_data(0)
    attrs = cf.get_trace_attrs(0)
    cf.set_trace_attrs(0, attrs)
    with pytest.raises(ValueError):
        cf.set_trace_attrs(1, attrs)
    with pytest.raises(ValueError):
        attrs["original_file"] = "invalid_filename.hdf5"
        cf.set_trace_attrs(1, attrs)
    with pytest.raises(ValueError):
        del attrs["original_file"]
        cf.set_trace_attrs(1, attrs)
