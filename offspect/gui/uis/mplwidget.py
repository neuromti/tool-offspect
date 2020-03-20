# -*- coding: utf-8 -*-
"""
In Designer, promote a default QWidget to MplWidget, with the header file being the path of this file relative to the .ui file, e.g. `.mplwidget.py`.

Subsequently, compile the ui-file with e.g :code:`pyuic5 visual_inspection_gui_<RESOLUTION>.ui > visual_inspection_gui_<RESOLUTION>.py` and you can use with this ui with the visual inspection GUI
"""


# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as image


class MplWidget(QWidget):  # type: ignore
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.setLayout(vertical_layout)

