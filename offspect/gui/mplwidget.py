# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:28:37 2020

@author: Ethan
"""


# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as image


class MplWidget1(QWidget):  # type: ignore
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.setLayout(vertical_layout)


class MplWidget2(QWidget):  # type: ignore
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.setLayout(vertical_layout)

