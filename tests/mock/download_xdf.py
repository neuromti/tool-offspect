import urllib.request
from pathlib import Path

xdf_urls = {
    "acute_nmes.xdf": "https://github.com/translationalneurosurgery/tool-offspect/releases/download/v0.1.0/acute_nmes.xdf",
    "acute_tms.xdf": "https://github.com/translationalneurosurgery/tool-offspect/releases/download/v0.1.0/acute_tms.xdf",
}


def download_to_file(url: str, fname: str):
    print(f"Beginning file download from {url}")
    urllib.request.urlretrieve(url, fname)


def mock(xdfname: str, clean=False):
    try:
        url = xdf_urls[xdfname]
    except KeyError:
        raise NotImplementedError(f"I do not know how to mock {xdfname}")

    fname = Path(__file__).parent.expanduser().absolute() / xdfname

    if clean and fname.exists():
        fname.unlink()

    if not fname.exists():
        download_to_file(url, str(fname))

    return str(fname)


if __name__ == "__main__":
    for fname in xdf_urls.keys():
        mock(fname, clean=True)
        print("Download complete for", fname)
