# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:47:23 2020

@author: Ethan
"""

from PyQt5.QtWidgets import *
<<<<<<< HEAD
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

=======
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
        
>>>>>>> 6e8bdbe39636a3d59a054b6b6ceb589a50a4fcec
