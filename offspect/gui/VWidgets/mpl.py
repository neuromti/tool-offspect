# -*- coding: utf-8 -*-
"""
In Designer, promote a default QWidget to MplWidget, with the header file being the path of this file relative to the .ui file, e.g. `.mplwidget.py`.

Subsequently, compile the ui-file with e.g :code:`pyuic5 visual_inspection_gui_<RESOLUTION>.ui > visual_inspection_gui_<RESOLUTION>.py` and you can use with this ui with the visual inspection GUI
"""


# from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as image
import matplotlib.pyplot as plt
from offspect.api import decode, CacheFile
from math import nan
import numpy as np


class MplWidget(QtWidgets.QWidget):
    def __init__(self, cf: CacheFile, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.cf = cf
        self.canvas = FigureCanvas(Figure())

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.setLayout(self.layout)


# ------------------------------------------------------------------------------
def plot_trace_on(ax, data, t0, t1, pre, post, shift=0):
    "plot trace data on an axes"
    x = np.arange(-pre, post) + shift
    ax.plot([0, 0], [-200, 200], ":r")
    ax.plot(x, data)
    ax.set_ylim(-200, 200)
    ax.grid(True, which="both")
    ax.set_xticks((-pre, 0, post))
    ax.set_xticklabels((t0, 0, t1))
    ax.set_xticks(range(0, pre + post, (pre + post) // 10), minor=True)
    ax.set_xlim(-pre, post)
    ax.tick_params(direction="in")


class TraceWidget(MplWidget):
    def __init__(self, cf: CacheFile, idx: int = 0, parent=None):
        super().__init__(cf=cf, parent=parent)
        self.plot_trace(idx)

    def plot_trace(self, idx: int = 0):
        data = self.cf.get_trace_data(idx)
        attrs = self.cf.get_trace_attrs(idx)
        pre = decode(attrs["samples_pre_event"])
        post = decode(attrs["samples_post_event"])
        fs = decode(attrs["samplingrate"])
        shift = decode(attrs["onset_shift"])
        shift = shift or 0
        t0 = -float(pre) / float(fs)
        t1 = float(post) / float(fs)
        plot_trace_on(self.canvas.axes, data, t0, t1, pre, post, shift)
        print(f"Plotting {idx} shifted by {shift}")
