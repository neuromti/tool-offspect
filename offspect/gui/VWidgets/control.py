from PyQt5 import QtWidgets
from offspect.api import CacheFile, decode, encode
from typing import Callable
from functools import partial
from offspect.cache.attrs import get_valid_trace_keys
from .textedit import VTextEdit


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
        for button in [self.prev_button, self.trace_idx_num, self.next_button]:
            buttonlayout.addWidget(button)

        idxlayout = QtWidgets.QHBoxLayout()
        for item in [self.reject_button]:
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
