from PyQt5 import QtWidgets
from offspect.api import CacheFile, decode, encode
from typing import Callable
from functools import partial
from offspect.cache.attrs import get_valid_trace_keys
from .textedit import VTextEdit
from offspect.gui.io import save


class IntegerAttribute(QtWidgets.QWidget):
    def read(self):
        text = self.line.text()
        try:
            text = str(int(text))
        except Exception:
            text = "0"
            self.line.setText(text)

        return str(text)

    def on_edit(self):
        save(cf=self.cf, idx=self.idx, key=self.key, read=self.read)
        self.callback()

    def draw_int(self, idx: int = 0):
        self.idx = idx
        tattr = self.cf.get_trace_attrs(self.idx)
        val = decode(tattr[self.key])
        val = val or 0
        if type(val) == str:
            val = 0
        elif type(val) == float:
            val = int(val)
        val = "{0:3.0f}".format(val)
        print(f"Loading {self.key}:{val} for {idx}")
        self.line.setText(val)

    def __init__(
        self,
        cf: CacheFile,
        idx: int = 0,
        key: str = "onset_shift",
        callback: Callable = lambda: None,
        parent=None,
    ):
        super().__init__()
        self.key = key
        self.cf = cf
        self.idx = idx
        self.callback = callback
        self.label = QtWidgets.QLabel(text=key.replace("_", " ").capitalize())
        self.line = QtWidgets.QLineEdit()
        self.draw_int(idx)
        self.line.editingFinished.connect(self.on_edit)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line)

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
        self.trace_idx_num.editingFinished.connect(self.refresh)
        self.reject_button.clicked.connect(self.flip_reject_button)
        self.prev_button.clicked.connect(self.click_prev)
        self.next_button.clicked.connect(self.click_next)

        self.buttonlayout = QtWidgets.QHBoxLayout()
        for button in [self.prev_button, self.trace_idx_num, self.next_button]:
            self.buttonlayout.addWidget(button)

        self.idxlayout = QtWidgets.QHBoxLayout()
        for item in [self.reject_button]:
            self.idxlayout.addWidget(item)

        self.onset_shift = IntegerAttribute(
            cf=self.cf, idx=self.trace_idx, key="onset_shift", callback=self.refresh
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.buttonlayout)
        layout.addLayout(self.idxlayout)
        layout.addWidget(self.onset_shift)
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
        print("Setting trace_idx from", self.trace_idx + 1, "to", trace_idx)
        self.trace_idx_num.setText(str(trace_idx))
        self.refresh()

    def check_trace_idx(self):
        self.trace_idx += 0

    def click_next(self):
        self.trace_idx += 1

    def click_prev(self):
        self.trace_idx -= 1

    def refresh(self):
        self.onset_shift.draw_int(self.trace_idx)
        self.draw_reject_button()
        self.callback()

    def draw_reject_button(self):
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
        self.draw_reject_button()
