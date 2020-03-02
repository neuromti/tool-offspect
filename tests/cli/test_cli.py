from subprocess import Popen, PIPE
import pytest
import time
from tempfile import NamedTemporaryFile
from pathlib import Path


def test_cli_merge(cachefile0, cachefile1):
    with NamedTemporaryFile(suffix=".hdf5", mode="wb") as _tf:
        tf = Path(_tf.name)
        p = Popen(
            [
                "offspect",
                "merge",
                "-f",
                str(cachefile0[0]),
                str(cachefile1[0]),
                "-t",
                tf.name,
                "-v",
            ],
            stdout=PIPE,
            stderr=PIPE,
        )
        assert tf.exists()
        time.sleep(1)
        o, e = p.communicate()
        assert tf.name in o.decode()  # successfull merge
        assert cachefile0[1]["origin"] in o.decode()  # successfull peek
        assert e == b""  # no errors


def test_cli_peek(cachefile0):
    p = Popen(["offspect", "peek", str(cachefile0[0])], stdout=PIPE, stderr=PIPE,)
    time.sleep(1)
    o, e = p.communicate()
    assert cachefile0[1]["origin"] in o.decode()
    assert e == b""  # no errors


def test_cli_none():
    p = Popen(["offspect"], stdout=PIPE, stderr=PIPE,)
    time.sleep(1)
    o, e = p.communicate()
    assert "No valid subcommand" in o.decode()
    assert e == b""  # no errors
