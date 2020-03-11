import pytest
import tempfile
from pathlib import Path
from .mock.cache import create_test_cachefile, get_cachefile_template


@pytest.fixture(scope="module")
def cachefile0():
    "create a temporary cachefile0 different to, but fully consistent with cachefile1"
    settings = get_cachefile_template()[0]
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as _tf:
        tf = Path(_tf.name)
        tf.unlink()
        assert tf.exists() == False
        create_test_cachefile(tf, settings)
        yield tf, settings
    assert tf.exists() == False


@pytest.fixture(scope="module")
def cachefile0inconsistent():
    "create a cachefile similar to, but inconsistent with cachefile0"
    settings = get_cachefile_template()[1].copy()
    settings["attrs"]["channel_labels"] = ["INVALID"]
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as _tf:
        tf = Path(_tf.name)
        tf.unlink()
        assert tf.exists() == False
        create_test_cachefile(tf, settings)
        yield tf, settings
    assert tf.exists() == False


@pytest.fixture(scope="module")
def cachefile1():
    "create a temporary cachefile1, different to, but fully consistent with cachefile0"
    settings = get_cachefile_template()[1]
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as _tf:
        tf = Path(_tf.name)
        tf.unlink()
        assert tf.exists() == False
        create_test_cachefile(tf, settings)
        yield tf, settings
    assert tf.exists() == False


@pytest.fixture(scope="session")
def matfile():
    yield Path(__file__).parent / "map_contralesional.mat"


@pytest.fixture(scope="session")
def xmlfile():
    yield Path(__file__).parent / "coords_contralesional.xml"
