# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:47:23 2020

@author: Ethan
"""

from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure


class Next_Button(QPushButton):
    def __init__(self, parent=None):

        QPushButton.__init__(self, parent)


class Previous_Button(QPushButton):
    def __init__(self, parent=None):

        QPushButton.__init__(self, parent)


class Reject_Button(QPushButton):
    def __init__(self, parent=None):

        QPushButton.__init__(self, parent)

