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
from matplotlib.patches import Polygon
from offspect.api import decode, CacheFile
from math import nan
import numpy as np


class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = FigureCanvas(Figure())

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.setLayout(self.layout)
        self.axes = self.canvas.axes


# ------------------------------------------------------------------------------
def plot_trace_on(ax, data, t0, t1, pre, post, mepidx, namp, pamp, shift=0):
    "plot trace data on an axes"
    x = np.arange(-pre, post) + shift
    onset = pre - shift
    ax.plot([0, 0], [-200, 200], ":r")
    peak = x[mepidx[0] + onset]
    ax.plot([peak, peak], [0, namp], "k")
    peak = x[mepidx[-1] + onset]
    ax.plot([peak, peak], [0, pamp], "k")

    facecolor = "0.8"
    if data[mepidx[0] + onset, 0] != namp:
        facecolor = "1"
        print("namp:", data[mepidx[0] + onset, 0], namp)
    if data[mepidx[-1] + onset, 0] != pamp:
        facecolor = "1"
        print("pamp:", data[mepidx[-1] + onset, 0], pamp)

    verts = []

    verts.append((x[mepidx[0] + onset], 0))
    for _x in mepidx:
        _y = data[_x + onset, 0]
        verts.append((x[_x + onset], _y))
    verts.append((x[mepidx[-1] + onset], 0))
    poly = Polygon(verts, facecolor=facecolor, edgecolor="0.5")
    ax.add_patch(poly)
    ax.plot(x, data)
    ax.set_ylim(-200, 200)
    ax.grid(True, which="both")
    ax.set_xticks((-pre, 0, post))
    ax.set_xticklabels((t0, 0, t1))
    ax.set_xticks(range(0, pre + post, (pre + post) // 10), minor=True)
    ax.set_xlim(-pre, post)
    ax.tick_params(direction="in")


class TraceWidget(QtWidgets.QWidget):
    def __init__(self, cf: CacheFile, idx: int = 0, parent=None):

        super().__init__(parent=parent)
        self.canvas = MplWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot_trace(cf, idx)

    def plot_trace(self, cf, idx: int = 0):
        data = cf.get_trace_data(idx)
        attrs = cf.get_trace_attrs(idx)
        pre = decode(attrs["samples_pre_event"])
        post = decode(attrs["samples_post_event"])
        fs = decode(attrs["samplingrate"])
        shift = decode(attrs["onset_shift"])
        shift = shift or 0
        t0 = -float(pre) / float(fs)
        t1 = float(post) / float(fs)
        nlat = int(decode(attrs["neg_peak_latency_ms"]) * float(fs) / 1000)
        plat = int(decode(attrs["pos_peak_latency_ms"]) * float(fs) / 1000)
        latencies = sorted([nlat, plat])
        mepidx = [idx for idx in range(latencies[0], latencies[1] + 1)]

        namp = decode(attrs["neg_peak_magnitude_uv"])
        pamp = decode(attrs["pos_peak_magnitude_uv"])

        plot_trace_on(
            self.canvas.axes, data, t0, t1, pre, post, mepidx, namp, pamp, shift
        )

        print(f"Plotting {idx} shifted by {shift}")
