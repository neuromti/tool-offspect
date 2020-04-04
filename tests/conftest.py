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
    print("Mocking matfile")
    yield Path(__file__).parent / "map_contralesional.mat"


@pytest.fixture(scope="session")
def xmlfile():
    print("Mocking xmlfile")
    yield Path(__file__).parent / "coords_contralesional.xml"


@pytest.fixture(scope="session")
def get_matprot():
    from .mock.mock_matprot import mock

    mocked = mock()
    for f in mocked:
        if Path(f).suffix == ".xml":
            xmlfile = f
        elif Path(f).suffix == ".mat":
            matfile = f
    yield xmlfile, matfile


@pytest.fixture(scope="session")
def get_xdffile():
    from .mock.mock_xdf import mock

    yield mock
