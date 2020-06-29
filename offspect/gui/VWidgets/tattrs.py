from PyQt5 import QtWidgets
from offspect.api import CacheFile, decode, encode
from typing import Callable
from functools import partial
from offspect.cache.attrs import get_valid_trace_keys
from .textedit import VTextEdit
from offspect.gui.io import save


class TattrWidget(QtWidgets.QWidget):
    """Widget listing all TraceAttributes
        

    Example::

        python -m offspect.gui.baseui stroke_map.hdf5  0
        python -m offspect.gui.baseui stroke_map.hdf5  0
    """

    def __init__(self, cf: CacheFile, idx: int, *args, **kwargs):
        super(TattrWidget, self).__init__(*args, **kwargs)

        tattrs = self.get_cleaned_tattrs(cf, idx)
        layout = QtWidgets.QGridLayout()
        row = 0
        for key in tattrs.keys():
            label = QtWidgets.QLabel(text=key.replace("_", " ").capitalize())
            if type(decode(tattrs[key])) == float:
                val = "{0:3.3f}".format(decode(tattrs[key]))
                line = QtWidgets.QLineEdit(val)
            else:
                line = QtWidgets.QLineEdit(tattrs[key])

            trig = partial(save, cf=cf, idx=idx, key=key, read=line.text)
            line.textChanged.connect(trig)
            layout.addWidget(label, row, 0)
            layout.addWidget(line, row, 1)
            row += 1

        key = "comment"
        tattrs = cf.get_trace_attrs(idx)
        label = QtWidgets.QLabel(text=key)
        line = VTextEdit(tattrs[key])
        trig = partial(save, cf=cf, idx=idx, key=key, read=line.toPlainText)
        line.editingFinished.connect(trig)
        layout.addWidget(label, row, 0)
        layout.addWidget(line, row, 1)

        self.setLayout(layout)

    def get_cleaned_tattrs(self, cf, idx):
        tattrs = cf.get_trace_attrs(idx)
        initialize_with_zero = [
            "onset_shift",
            "neg_peak_latency_ms",
            "pos_peak_latency_ms",
            "neg_peak_magnitude_uv",
            "pos_peak_magnitude_uv",
        ]
        for key in initialize_with_zero:
            tattrs[key] = encode(decode(tattrs[key]) or 0)
        cf.set_trace_attrs(idx, tattrs)
        keys = get_valid_trace_keys(tattrs["readin"], tattrs["readout"]).copy()
        keys.remove("reject")
        keys.remove("onset_shift")
        keys.remove("comment")
        show_tattrs = dict()
        for key in sorted(keys):
            if key[0] != "_":
                show_tattrs[key] = tattrs[key]
        return show_tattrs
