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
        tattr = cf.get_trace_attrs(idx)
        keys = get_valid_trace_keys(tattr["readin"], tattr["readout"]).copy()
        keys.remove("reject")
        keys.remove("onset_shift")
        keys.remove("comment")
        layout = QtWidgets.QGridLayout()
        row = 0
        for key in sorted(keys):
            label = QtWidgets.QLabel(text=key.replace("_", " ").capitalize())
            if type(decode(tattr[key])) == float:
                val = "{0:3.3f}".format(decode(tattr[key]))
                line = QtWidgets.QLineEdit(val)
            else:
                line = QtWidgets.QLineEdit(tattr[key])

            trig = partial(save, cf=cf, idx=idx, key=key, read=line.text)
            line.textChanged.connect(trig)
            layout.addWidget(label, row, 0)
            layout.addWidget(line, row, 1)
            row += 1

        key = "comment"
        label = QtWidgets.QLabel(text=key)
        line = VTextEdit(tattr[key])
        trig = partial(save, cf=cf, idx=idx, key=key, read=line.toPlainText)
        line.editingFinished.connect(trig)
        layout.addWidget(label, row, 0)
        layout.addWidget(line, row, 1)

        self.setLayout(layout)
