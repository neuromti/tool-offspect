"""
Mock and test smartmove
-----------------------

:code-block: bash

    python mock_smartmove.py .
    
    offspect tms -t test.hdf5 -f documentation.txt VvNn_VvNn_2000-12-31_23-59-59.cnt "VvNn 2000-12-31_23-59-59.cnt" -r contralateral_mep -c Ch1 -pp 100 100

"""

import libeep
from pathlib import Path
import numpy as np
import shutil
import sys


def mock(folder: Path):

    folder.mkdir(exist_ok=True)
    fname = folder / "VvNn 2000-12-31_23-59-59.cnt"
    if fname.exists():
        fname.unlink()
    fname = str(fname)
    rate = 1024
    channel_count = 8
    channels = [(f"Ch{i}", "None", "uV") for i in range(1, channel_count + 1, 1)]
    c = libeep.cnt_out(fname, rate, channels)
    samples = np.repeat(np.arange(0, 5000), 8).flatten().tolist()
    c.add_samples(samples)
    c.close()

    fname = folder / "VvNn_VvNn_2000-12-31_23-59-59.cnt"
    if fname.exists():
        fname.unlink()
    fname = str(fname)
    rate = 1000
    channel_count = 64
    channels = [(f"EEG{i}", "None", "uV") for i in range(1, channel_count + 1, 1)]
    c = libeep.cnt_out(fname, rate, channels)
    samples = np.repeat(np.arange(0, 5000), 8).flatten().tolist()
    c.add_samples(samples)
    tstamps = (1000, 2048)
    for t in tstamps:
        c.add_trigger(t, "0001")
    c.close()

    docfile = Path(__file__).parent / "documentation.txt"
    shutil.copy(docfile, folder)


if __name__ == "__main__":
    mock(Path(sys.argv[1]))
