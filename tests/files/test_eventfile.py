import pytest
from pathlib import Path
import pkg_resources
from offspect.cache import efile


@pytest.fixture(scope="module")
def ymls():
    root = pkg_resources.resource_filename("offspect", "")
    fname = Path(root) / "templates/events_<identifier>.yml"
    assert fname.exists()
    ymls = efile.load(fname)
    yield ymls


def test_efile_invalid():
    with pytest.raises(Exception):
        efile.load("events_invalid.wrong")

    with pytest.raises(Exception):
        efile.load("wrong_invalid.yml")


def test_efiles_merged(ymls):
    assert len(ymls) == 2


def test_efiles_reject_is_bool(ymls):
    assert type(ymls[0]["traces"][0]["reject"]) == bool
