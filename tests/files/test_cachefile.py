import pytest
import tempfile
from pathlib import Path
from offspect.cache.hdf import create_test_cachefile, CacheFile


@pytest.fixture(scope="module")
def cachefile():
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as _tf:
        tf = Path(_tf.name)
        tf.unlink()
        assert tf.exists() == False
        create_test_cachefile(tf)
        yield tf
    assert tf.exists() == False


def test_cache_tmp_exists(cachefile):
    assert cachefile.exists()
    cf = CacheFile(cachefile)
