import pytest
import tempfile
from pathlib import Path
from mock.cache import create_test_cachefile, get_cachefile_template

# import sys
# sys.path.append(Path(__file__).parent)


@pytest.fixture(scope="module")
def cachefile0():
    settings = get_cachefile_template()[0]
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as _tf:
        tf = Path(_tf.name)
        tf.unlink()
        assert tf.exists() == False
        create_test_cachefile(tf, settings)
        yield tf, settings
    assert tf.exists() == False


@pytest.fixture(scope="module")
def cachefile1():
    settings = get_cachefile_template()[1]
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as _tf:
        tf = Path(_tf.name)
        tf.unlink()
        assert tf.exists() == False
        create_test_cachefile(tf, settings)
        yield tf, settings
    assert tf.exists() == False
