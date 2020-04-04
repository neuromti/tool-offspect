import pytest
from offspect.input.tms.xdfprot import *
from pathlib import Path


def test_convert_xdf(xdffile):
    fname = xdffile("acute_nmes.xdf")
    print(fname)
