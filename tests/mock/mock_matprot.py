"""
Mock and test matprot 
---------------------


:code-block: bash

    offspect tms -t test.hdf5 -f /media/rgugg/tools/python3/tool-load-tms/tests/coords_contralesional.xml /media/rgugg/tools/python3/tool-load-tms/tests/map_contralesional.mat -pp 100 100 -r contralateral_mep -c EDC_L
"""
import urllib.request
import zipfile
from pathlib import Path
from typing import List


def download_and_unzip(url: str, folder: Path, clean=False) -> List[str]:
    fname = folder / "matprot.zip"
    urllib.request.urlretrieve(url, fname)
    with zipfile.ZipFile(str(fname), "r") as zf:
        members = zf.namelist()
        for m in members:
            if (folder / m).exists() and clean:
                (folder / m).unlink()

            if (folder / m).exists():
                print(f"{m} already exists")
            else:
                print("Unzipping", m)
                zf.extract(m, path=str(folder))

    fname.unlink()
    return [str(folder / m) for m in members]


def mock(clean=False):
    folder = Path(__file__).parent.expanduser().absolute()
    url = "https://github.com/translationalneurosurgery/tool-offspect/releases/download/v0.1.0/matprot.zip"
    members = download_and_unzip(url, folder, clean=clean)
    return members


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == True:
        clean = True
    else:
        clean = False
    mock(clean)
