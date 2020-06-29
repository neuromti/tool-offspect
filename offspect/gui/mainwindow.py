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
from tempfile import mkdtemp
from pathlib import Path
from offspect.cache.steps import process_data
from offspect.cache.file import write_tracedata, encode


def close_tmpdir(tmpdir):
    import shutil

    shutil.rmtree(tmpdir)
    print(f"ENV: Cleared temporary directory {tmpdir}")


def open_tmpdir():
    import atexit

    tmpdir = Path(mkdtemp())
    print(f"ENV: Created temporary directory {tmpdir}")
    atexit.register(lambda: close_tmpdir(tmpdir))
    return tmpdir


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, filename=None, idx: int = 0):
        super(MainWindow, self).__init__(parent)
        self.tmpdir = open_tmpdir()
        self.load_cache_file(filename, idx)
        self.setWindowTitle(str(filename))

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("&File")

        apply = QtWidgets.QAction("&Apply", self)
        apply.setShortcut("Ctrl+A")
        apply.setToolTip(
            "Applies all preprocessing steps to this trace and writes them permanently into the CacheFile"
        )
        apply.triggered.connect(self.save_tracedata)

        load = QtWidgets.QAction("&Open", self)
        load.setShortcut("Ctrl+O")
        load.setToolTip("Open a new CacheFile")
        load.triggered.connect(lambda: self.load_cache_file(None, 0))

        fileMenu.addAction(apply)
        fileMenu.addAction(load)
        fileMenu.setToolTipsVisible(True)

    def load_cache_file(self, filename=None, idx: int = 0):
        if filename is None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open file", "/", "CacheFiles (*.hdf5)"
            )
            if filename is not "":
                self.filename = filename
        else:
            self.filename = filename
        print("Opening", self.filename)
        self.cf = CacheFile(self.filename)

        self.ctrl = VWidgets.ControlWidget(cf=self.cf, idx=idx)
        self.ctrl.callback = self.refresh
        self.refresh()
        print(f"GUI: Loading {self.filename}")

    def save_tracedata(self):
        idx = self.ctrl.trace_idx
        data = self.cf.get_trace_data(idx)
        attrs = self.cf.get_trace_attrs(idx)
        data = process_data(data, attrs, key="_log")
        write_tracedata(self.cf, data, idx)
        attrs["_log"] = encode([])
        print("Applied preprocessing and wrote into CacheFile")
        self.cf.set_trace_attrs(idx, attrs)

    def refresh(self):
        print("GUI: Refreshing GUI for new trace")
        self.trc = VWidgets.TraceWidget(cf=self.cf, idx=self.ctrl.trace_idx)
        self.coords = VWidgets.CoordsWidget(
            cf=self.cf, idx=self.ctrl.trace_idx, tmpdir=self.tmpdir
        )
        self.tattr = VWidgets.TattrWidget(cf=self.cf, idx=self.ctrl.trace_idx)
        self.oattr = VWidgets.OattrWidget(cf=self.cf, idx=self.ctrl.trace_idx)

        right_column = QtWidgets.QWidget()
        lt = QtWidgets.QVBoxLayout()
        lt.addWidget(self.oattr)
        lt.addWidget(self.coords)
        right_column.setLayout(lt)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.tattr, 0, 0, 2, 1)
        layout.addWidget(self.ctrl, 0, 1, 1, 1)
        layout.addWidget(self.trc, 1, 1, 1, 1)
        layout.addWidget(right_column, 0, 2, 2, 1)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
