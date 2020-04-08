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
from offspect.api import decode
from math import nan


class MplWidget(QtWidgets.QWidget):  # type: ignore
    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.setLayout(vertical_layout)


def plot_trace_on(ax, data, attrs):

    pre = decode(attrs["samples_pre_event"])
    post = decode(attrs["samples_post_event"])
    fs = decode(attrs["samplingrate"])
    t0 = -float(pre) / float(fs)
    t1 = float(post) / float(fs)

    # plot data
    ax.plot(data)
    ax.set_ylim(-200, 200)
    ax.grid(True, which="both")
    ax.set_xticks((0, pre, pre + post))
    ax.set_xticklabels((t0, 0, t1))
    ax.set_xticks(range(0, pre + post, (pre + post) // 10), minor=True)
    ax.tick_params(direction="in")
