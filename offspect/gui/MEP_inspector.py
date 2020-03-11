# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:28:37 2020

@author: Ethan
"""
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, uic
import visual_inspection_gui
import sys
from os import chdir
from pathlib import Path
from functools import partial
from matplotlib import pyplot as plt
import time
from scipy import stats
import numpy as np
import liesl
import configparser
import matplotlib
import matplotlib.image as image
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')
matplotlib.rcParams['axes.linewidth'] = 0.1

def on_close():
   print("Shutting down")

class Ui(QtWidgets.QMainWindow, visual_inspection_gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Ui, self).__init__(parent)
        self.setupUi(self)
        self.addToolBar(NavigationToolbar(self.MplWidget1.canvas, self))
        self.addToolBar(NavigationToolbar(self.MplWidget2.canvas, self))
        self.plot_mep()
        self.plot_coil_coordinates()
        
#        self.reject_checkbox.clicked.connect(print('rejected'))
#        self.previous_button.clicked.connect(print('back'))
        self.next_button.clicked.connect(self.plot_mep)
        
    def plot_mep(self):
        
        # discards the old graph
        self.MplWidget1.canvas.axes.clear()
        
        data    = np.random.rand(500)
        data    = stats.zscore(data)
        peakpos = [data.argmin(), data.argmax()]
        val     = [data.min(), data.max()]
        vpp     = val[1] - val[0]
        wndw    = [np.min(peakpos) - 200, np.max(peakpos) + 200]
        timey   = np.arange(0, len(data))

        # plot data
        self.MplWidget1.canvas.axes.plot(timey[wndw[0] : wndw[1]], data[wndw[0] : wndw[1]])
        
        self.MplWidget1.canvas.axes.vlines(
            [timey[peakpos[0]]], val[0], np.mean(data), color="red", linestyle="dashed")
        self.MplWidget1.canvas.axes.vlines(
            [timey[peakpos[1]]], val[1], np.mean(data), color="red", linestyle="dashed")

        textstr = "Vpp = {0:3.2f}".format(vpp)
        props   = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

        self.MplWidget1.canvas.axes.text(
            0.05,
            0.95,
            textstr,
            transform=self.MplWidget1.canvas.axes.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props)
        time.sleep(0.01)
                
        # refresh canvas
        self.MplWidget1.canvas.draw()

    def plot_coil_coordinates(self):
        
        # discards the old graph
        self.MplWidget2.canvas.axes.clear()
        
        im = image.imread('coilpic.png')
        brain = image.imread('brain.png')
        
        self.MplWidget2.canvas.axes.imshow(brain, aspect='auto', extent=(-1, 7, -4, 7), zorder=1)
        
        import itertools
        r = 6
        c = 6
        x = np.linspace(0, c, c+1)
        y = np.linspace(0, r, r+1)
        
        pts = itertools.product(x, y)
        
        current_coil_location = [4,5]
        # plot current coordinates
        self.MplWidget2.canvas.axes.plot(current_coil_location[0], current_coil_location[1], "ro", zorder=3)
        coilcoor = (current_coil_location[0],current_coil_location[0]+3, current_coil_location[1]-0.4, current_coil_location[1]+2) 
        self.MplWidget2.canvas.axes.imshow(
                im, aspect='auto', extent=coilcoor, zorder=2)
        
        # plot grid
        self.MplWidget2.canvas.axes.scatter(*zip(*pts), marker='o', s=30, color='blue', zorder=3)
        self.MplWidget2.canvas.axes.set_ylabel("Dorsal - Ventral")
        self.MplWidget2.canvas.axes.set_xlabel("Anterior - Posterior")
        
        self.MplWidget2.canvas.axes.set_xticks([])
        self.MplWidget2.canvas.axes.set_yticks([])
        
        textstr = str("Location: " + str((current_coil_location[0], current_coil_location[1])))
        props   = dict(boxstyle="round", facecolor="wheat", alpha=1)

        self.MplWidget2.canvas.axes.text(
            0.05,
            0.95,
            textstr,
            transform=self.MplWidget2.canvas.axes.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props)
        # refresh canvas
        self.MplWidget2.canvas.draw()

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            app.exit()
        else:
            event.ignore()

#%%
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
    
