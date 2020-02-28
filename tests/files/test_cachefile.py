import pytest
import tempfile
from pathlib import Path
from offspect.cache import file as hdf


@pytest.fixture(scope="module")
def cachefile():
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as _tf:
        tf = Path(_tf.name)
        tf.unlink()
        assert tf.exists() == False
        hdf.create_test_cachefile(tf)
        yield tf
    assert tf.exists() == False


def test_cache_tmp_attributes(cachefile):
    assert cachefile.exists()
    cf = hdf.CacheFile(cachefile)
    ymls = hdf._get_cachefile_template()
    assert len(ymls) == len(ymls)
    assert ymls[0]["origin"] == cf.traces[0][0]["origin"]
    exp_trace_count = sum([len(yml["traces"]) for yml in ymls])
    assert exp_trace_count == len(cf.traces)
