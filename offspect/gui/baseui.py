from PyQt5 import QtCore, QtGui, QtWidgets
from offspect.api import CacheFile
from offspect.cache.attrs import (
    AnnotationDictionary,
    decode,
    encode,
    get_valid_trace_keys,
)
from typing import Dict, Callable
from offspect.cache.readout import valid_origin_keys, must_be_identical_in_merged_file
from functools import partial
from offspect.gui import VWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, filename=None, idx: int = 0):
        super(MainWindow, self).__init__(parent)
        self.load_cache_file(filename, idx)

    def load_cache_file(self, filename=None, idx: int = 0):
        if filename is None:
            self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open file", "/", "CacheFiles (*.hdf5)"
            )
        else:
            self.filename = filename
        self.cf = CacheFile(self.filename)
        self.c = VWidgets.ControlWidget(cf=self.cf, idx=idx)
        self.c.callback = self.refresh
        self.refresh()
        print(f"GUI: Loading {self.filename}")

    def refresh(self):
        self.t = VWidgets.TraceWidget(cf=self.cf, idx=self.c.trace_idx)
        self.w = VWidgets.TattrWidget(cf=self.cf, idx=self.c.trace_idx)
        self.o = VWidgets.OattrWidget(cf=self.cf, idx=self.c.trace_idx)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.w, 0, 0, 2, 1)
        layout.addWidget(self.c, 0, 1, 1, 1)
        layout.addWidget(self.t, 1, 1, 1, 1)
        layout.addWidget(self.o, 0, 2, 2, 1)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])
    tattr = {"test": "this", "and": "that"}
    # w = TattrWidget(cf=CacheFile(sys.argv[1]), idx=int(sys.argv[2]))
    # w.show()

    # o = OattrWidget(cf=CacheFile(sys.argv[1]), idx=int(sys.argv[2]))
    # o.show()

    # c = ControlWidget(filename=sys.argv[1])
    # c.show()

    ui = MainWindow(filename=sys.argv[1], idx=int(sys.argv[2]) - 1)
    ui.show()

    app.exec_()
