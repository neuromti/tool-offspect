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
from offspect.gui import OfWidgets


def save(cf, idx: int, key: str, read: Callable):
    tattr = cf.get_trace_attrs(idx)
    text = read()
    if tattr[key] == text:
        return
    else:
        tattr[key] = encode(text)
        cf.set_trace_attrs(idx, tattr)
        print(f"CF: Wrote {idx}: {key} {text}")


def save_global(cf, idx: int, key: str, read: Callable):
    tattr = cf.get_trace_attrs(idx)
    text = read()
    if tattr[key] == text:
        return
    else:
        origin = tattr["origin"]
        for idx in range(len(cf)):
            tattr = cf.get_trace_attrs(idx)
            if tattr["origin"] == origin:
                tattr[key] = encode(text)
                cf.set_trace_attrs(idx, tattr)
        print(f"CF: Wrote globaly {origin}: {key} {text}")


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
        line = OfWidgets.OTextEdit(tattr[key])
        trig = partial(save, cf=cf, idx=idx, key=key, read=line.toPlainText)
        line.editingFinished.connect(trig)
        layout.addWidget(label, row, 0)
        layout.addWidget(line, row, 1)

        self.setLayout(layout)


class OattrWidget(QtWidgets.QWidget):
    """Widget listing all Origin Attributes
        

    Example::

        python -m offspect.gui.baseui stroke_map.hdf5  0
        python -m offspect.gui.baseui stroke_mep.hdf5  0
    """

    def __init__(self, cf: CacheFile, idx: int, *args, **kwargs):
        super(OattrWidget, self).__init__(*args, **kwargs)
        tattr = cf.get_trace_attrs(idx)
        layout = QtWidgets.QGridLayout()
        keys = sorted(valid_origin_keys).copy()
        keys.remove("global_comment")
        keys.remove("channel_labels")

        row = 0
        for key in keys:
            label = QtWidgets.QLabel(text=key)
            line = QtWidgets.QLabel(tattr[key])
            layout.addWidget(label, row, 0)
            layout.addWidget(line, row, 1)
            row += 1

        key = "channel_labels"
        label = QtWidgets.QLabel(text=key)
        line = QtWidgets.QListWidget()
        entries = decode(tattr[key])
        line.addItems(entries)
        line.setFlow(line.LeftToRight)
        line.setMaximumHeight(50)
        layout.addWidget(label, row, 0)
        layout.addWidget(line, row, 1)

        row += 1
        key = "global_comment"
        label = QtWidgets.QLabel(text=key)
        line = OfWidgets.OTextEdit(tattr[key])
        trig = partial(save_global, cf=cf, idx=idx, key=key, read=line.toPlainText)
        line.editingFinished.connect(trig)
        layout.addWidget(label, row, 0)
        layout.addWidget(line, row, 1)

        self.setLayout(layout)


class ControlWidget(QtWidgets.QWidget):
    def __init__(self, cf=None, idx: int = 1, callback=lambda: None, *args, **kwargs):
        super(ControlWidget, self).__init__(*args, **kwargs)
        self.callback = callback
        self.cf = cf
        self.next_button = QtWidgets.QPushButton(text="Next")
        self.prev_button = QtWidgets.QPushButton(text="Prev")
        self.reject_button = QtWidgets.QPushButton(text="Reject")
        self.trace_idx_num = QtWidgets.QLineEdit(text=str(idx))

        self.trace_idx_num.editingFinished.connect(self.check_trace_idx)
        self.reject_button.clicked.connect(self.flip_reject_button)
        self.prev_button.clicked.connect(self.click_previous_button)
        self.next_button.clicked.connect(self.click_next_button)

        buttonlayout = QtWidgets.QHBoxLayout()
        for button in [self.prev_button, self.reject_button, self.next_button]:
            buttonlayout.addWidget(button)

        idxlayout = QtWidgets.QHBoxLayout()
        for item in [self.trace_idx_num]:
            idxlayout.addWidget(item)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(buttonlayout)
        layout.addLayout(idxlayout)
        self.setLayout(layout)
        self.trace_idx = idx

    @property
    def trace_idx(self):
        try:
            trace_idx = int(float(self.trace_idx_num.text())) - 1
        except ValueError:
            trace_idx = 0
        trace_idx = max((trace_idx, 0))
        trace_idx = min((trace_idx, len(self.cf) - 1))
        return trace_idx  # correct for the display starting counting at 1, not zero

    @trace_idx.setter
    def trace_idx(self, trace_idx: int):
        trace_idx += 1  # add one to start displaying at 1, not zero
        maxidx = len(self.cf)
        if trace_idx >= maxidx:
            trace_idx = maxidx
            self.next_button.setEnabled(False)
            self.prev_button.setEnabled(True)
        elif trace_idx <= 1:
            trace_idx = 1
            self.next_button.setEnabled(True)
            self.prev_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)
        print("Setting trace_idx from", self.trace_idx, "to", trace_idx)
        self.trace_idx_num.setText(str(trace_idx))
        self.set_reject_button()
        self.callback()

    def check_trace_idx(self):
        self.trace_idx += 0

    def click_next_button(self):
        self.trace_idx += 1

    def click_previous_button(self):
        self.trace_idx -= 1

    def set_reject_button(self):
        tattrs = self.cf.get_trace_attrs(self.trace_idx)
        reject = decode(tattrs["reject"])
        reject = False if reject is None else reject
        self.cf.set_trace_attrs(self.trace_idx, tattrs)
        if reject:
            self.reject_button.setStyleSheet("background-color: red")
            self.reject_button.setText("Rejected")
        else:
            self.reject_button.setStyleSheet("background-color: green")
            self.reject_button.setText("Accepted")

    def flip_reject_button(self):
        tattrs = self.cf.get_trace_attrs(self.trace_idx)
        reject = decode(tattrs["reject"])
        reject = True if reject is None else not reject
        tattrs["reject"] = reject
        self.cf.set_trace_attrs(self.trace_idx, tattrs)
        self.set_reject_button()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, filename=None, idx: int = 0):
        super(MainWindow, self).__init__(parent)
        if filename is None:
            self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open file", "/", "CacheFiles (*.hdf5)"
            )
        else:
            self.filename = filename
        print(f"GUI: Loading {self.filename}")
        refresh = QtWidgets.QAction(text="Refresh", parent=self, triggered=self.refresh)

        self.cf = CacheFile(self.filename)
        self.c = ControlWidget(cf=self.cf, idx=idx)
        self.c.callback = refresh.trigger
        self.refresh()

    def refresh(self):
        self.w = TattrWidget(cf=self.cf, idx=self.c.trace_idx)
        self.o = OattrWidget(cf=self.cf, idx=self.c.trace_idx)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.w)
        layout.addWidget(self.c)
        layout.addWidget(self.o)
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
