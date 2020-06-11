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
def plot_trace_on(ax, data, t0, t1, pre, post, lats, amps, shift=0):
    "plot trace data on an axes"
    x = np.arange(-pre, post) + shift
    onset = pre - shift
    ax.plot([0, 0], [-200, 200], ":r")
    peak = x[lats[0] + onset]
    ax.plot([peak, peak], [0, amps[0]], "k")
    peak = x[lats[1] + onset]
    ax.plot([peak, peak], [0, amps[1]], "k")

    facecolor = "0.8"
    if data[lats[0] + onset] != amps[0]:
        facecolor = "1"
        print("PLOT: First estimate deviates:", data[lats[0] + onset], amps[0])
    if data[lats[1] + onset] != amps[1]:
        facecolor = "1"
        print("PLOT: Second estimate deviates:", data[lats[-1] + onset], amps[1])
    if facecolor == "0.8":
        print("PLOT: Estimates in order")

    verts = []
    verts.append((x[lats[0] + onset], 0))
    for _x in range(lats[0], lats[1], 1):
        _y = data[_x + onset]
        verts.append((x[_x + onset], _y))
    verts.append((x[lats[1] + onset], 0))
    poly = Polygon(verts, facecolor=facecolor, edgecolor="0.5")
    ax.add_patch(poly)
    ax.plot(x, data)

    ylim = np.ceil(max(max(abs(data[onset + 10 :])), 20) / 10) * 10
    yticks = np.linspace(-ylim, ylim, 11)
    ax.set_yticks(yticks)
    ax.set_ylim(-ylim, ylim)
    ax.set_ylabel("Amplitude in microvolt")

    xticks = [-pre] + np.linspace(0, post, 6).tolist()
    xticklabels = [t0] + np.linspace(0, t1, 6).tolist()
    xticklabels = [t * 1000 for t in xticklabels]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(-pre, post)
    ax.set_xlabel("Time in ms relative to TMS")

    ax.grid(True, which="both")
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

        nlat = decode(attrs["neg_peak_latency_ms"]) or 0.0
        plat = decode(attrs["pos_peak_latency_ms"]) or 1.0
        namp = decode(attrs["neg_peak_magnitude_uv"]) or 0.0
        pamp = decode(attrs["pos_peak_magnitude_uv"]) or 0.0

        nlat = int(nlat * float(fs) / 1000)
        plat = int(plat * float(fs) / 1000)
        if nlat < plat:
            amps = (namp, pamp)
            lats = (nlat, plat)
        else:
            amps = (pamp, namp)
            lats = (plat, nlat)
        try:
            plot_trace_on(self.canvas.axes, data, t0, t1, pre, post, lats, amps, shift)
            print(f"PLOT: Plotting trace number {idx+1} shifted by {shift} samples")
        except Exception as e:
            print(e)
