# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:28:37 2020

@author: Ethan
"""

from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

class MplWidget1(QWidget):
    
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout() 
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.figure.tight_layout()
        self.setLayout(vertical_layout)
        
class MplWidget2(QWidget):
    
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout() 
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes = self.canvas.figure.add_subplot(111) 
        self.setLayout(vertical_layout)