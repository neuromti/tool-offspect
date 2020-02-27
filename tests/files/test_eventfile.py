import pytest
from pathlib import Path
import pkg_resources
from offspect.cache import efile


def test_loading_efile():
    root = pkg_resources.resource_filename("offspect", "")
    fname = Path(root) / "templates/events_<identifier>.yml"
    print(fname)
    assert fname.exists()
    ymls = efile.load(fname)
    assert len(ymls) == 2
