import pytest
from offspect.input.tms.smartmove import *
from tempfile import mkdtemp


@pytest.fixture
def doctxt():
    f = Path(__file__).parent.parent.parent / "mock" / "documentation.txt"
    yield str(f)


def test_load_document_txt_raises(doctxt, tmpdir):
    erroneous = tmpdir.mkdir("smartmove") / "documentation.txt"
    with Path(doctxt).open("r") as f:
        lines = f.readlines()

    lines[14] = "off"  # subject is different
    with erroneous.open("w") as f:
        f.write("".join(lines))
    with pytest.raises(ValueError):
        load_documentation_txt(str(erroneous))

    lines[13] = "off"  # experiment is different
    with erroneous.open("w") as f:
        f.write("".join(lines))
    with pytest.raises(ValueError):
        load_documentation_txt(str(erroneous))

    lines[8] = "3"  # index is wrong
    with erroneous.open("w") as f:
        f.write("".join(lines))
    with pytest.raises(ValueError):
        load_documentation_txt(str(erroneous))


def test_load_document_txt(doctxt):
    with pytest.raises(ValueError):
        load_documentation_txt("invalid.txt")
    load_documentation_txt(doctxt)
