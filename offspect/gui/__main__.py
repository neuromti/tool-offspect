# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:28:37 2020

@author: Ethan
"""
from PyQt5 import QtWidgets, QtGui
from offspect.gui import visual_inspection_gui
import sys
import os
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
        FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar,
    )
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar,
    )
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from offspect.api import CacheFile


# Ensure using PyQt5 backend
matplotlib.use("QT5Agg")
matplotlib.rcParams["axes.linewidth"] = 0.1

class Ui(QtWidgets.QMainWindow, visual_inspection_gui.Ui_MainWindow):
    def __init__(self, filename, parent=None):
        super(Ui, self).__init__(parent)
        self.setupUi(self)
        self.addToolBar(NavigationToolbar(self.MplWidget1.canvas, self))

        self.reject_button.setCheckable(True)
        self.reject_button.clicked.connect(self.update_reject_button)
        self.previous_button.clicked.connect(self.update_previous_button)
        self.next_button.clicked.connect(self.update_next_button)
        self.update_attrs_button.clicked.connect(self.update_attributes)
#        self.update_coil_button.clicked.connect(self.update_coil_coordinates)

        self.cf = CacheFile(filename)
        self.trace_idx = 0 # start with the first trace
        self.get_trace_from_cache()
        self.pull_attrs_info()
        self.attrs = self.cf.get_trace_attrs(self.trace_idx)
        self.initialize_reject_button()
        
    def update_attributes(self):
        self.attrs['neg_peak_magnitude_uv']      = float(self.troughmag_num.text())
        self.attrs['neg_peak_latency_ms']        = float(self.troughlat_num.text())
        self.attrs['pos_peak_latency_ms']        = float(self.peaklat_num.text())
        self.attrs['pos_peak_magnitude_uv']      = float(self.peakmag_num.text())
        self.attrs['zcr_latency_ms']             = float(self.zcr_lat_num.text())
        self.attrs['stimulation_intensity_mso']  = int(self.stimintensity_num.text())
        self.attrs['time_since_last_pulse_in_s'] = float(self.time_since_pulse_num.text())
        self.attrs['stimulation_intensity_didt'] = int(self.didt_num.text())
        self.attrs['comment']                    = str(self.commentbox.toPlainText())
        
        self.cf.set_trace_attrs(self.trace_idx, self.attrs)
    
    def initialize_reject_button(self):
        if self.attrs['reject'] == True:
            self.reject_button.setStyleSheet("background-color: red")
        elif self.attrs['reject'] == False:
            self.reject_button.setStyleSheet("background-color: light gray")
        
    def update_reject_button(self):
        '''
        flip rejection
        '''
        if self.attrs['reject'] == False:
            self.reject_button.setStyleSheet("background-color: red")
            self.attrs['reject'] = True
        elif self.attrs['reject'] == True:
            self.reject_button.setStyleSheet("background-color: light gray")
            self.attrs['reject'] = False
        self.cf.set_trace_attrs(self.trace_idx, self.attrs)
        
    def pull_attrs_info(self):
        self.attrs = self.cf.get_trace_attrs(self.trace_idx)
        
        for idx, val in enumerate(self.attrs):    
            if not attrs[self.val]:
                attrs[self.val] = 'No Value'
        
        self.event_time_num.display(self.attrs['event_time'])
        self.event_id_num.display(self.attrs['id'])
        self.troughmag_num.setText(str(self.attrs['neg_peak_magnitude_uv']))
        self.troughlat_num.setText(str(self.attrs['neg_peak_latency_ms']))
        self.peaklat_num.setText(str(self.attrs['pos_peak_latency_ms']))
        self.peakmag_num.setText(str(self.attrs['pos_peak_magnitude_uv']))
        self.zcr_lat_num.setText(str(self.attrs['zcr_latency_ms']))
        self.stimintensity_num.setText(str(self.attrs['stimulation_intensity_mso']))
        self.time_since_pulse_num.setText(str(self.attrs['time_since_last_pulse_in_s']))
        self.didt_num.setText(str(self.attrs['stimulation_intensity_didt']))
        
        self.channel_label.setText(self.attrs['channel_labels'][0])
        self.filename.setText(self.attrs['original_file'])
        self.examiner_name.setText(self.attrs['examiner'])
        self.readout.setText(self.attrs['readout'])
        
        self.commentbox.setText(self.attrs['comment'])
        
 
    def update_next_button(self):
        try:
            self.trace_idx += 1
            self.get_trace_from_cache()
            self.plot_mep()
            self.pull_attrs_info()
            self.initialize_reject_button()
            self.next_button.setStyleSheet("background-color: light gray")
        except:
            self.next_button.setStyleSheet("background-color: red")
        
    def update_previous_button(self):
        try:
            self.trace_idx -= 1
            self.get_trace_from_cache()
            self.plot_mep()
            self.pull_attrs_info()
            self.initialize_reject_button()
            self.previous_button.setStyleSheet("background-color: light gray")
        except:
            self.previous_button.setStyleSheet("background-color: red")
        
    def get_trace_from_cache(self):
        self.trace = self.cf.get_trace_data(self.trace_idx)
        self.plot_mep()

    def plot_mep(self):
        data = self.trace
        # discards the old graph
        self.MplWidget1.canvas.axes.clear()
        # plot data
        self.MplWidget1.canvas.axes.plot(data)
        # refresh canvas
        self.MplWidget1.canvas.draw()

#    def update_coil_coordinates(self):
#        a = int(self.coil_coordinate_input.text()[0])
#        b = int(self.coil_coordinate_input.text()[2])
#        if type(a) and type(b) != int:
#            self.next_button.setStyleSheet(
#                "QPushButton:pressed { background-color: red }"
#            )
#        else:
#            self.next_button.setStyleSheet(
#                "QPushButton:pressed { background-color: light gray }"
#            )
#        self.current_coil_location = [a, b]
#        self.plot_coil_coordinates()
#
#    def plot_coil_coordinates(self):
#        
#        if "win" in sys.platform:
#            cwd = os.path.abspath(os.path.dirname(sys.argv[0]))
#            im = image.imread(str(cwd + "\coilpic.png"))
#            brain = image.imread(str(cwd + "\map.png"))
#        else:
#            cwd = Path('__file__').parent
#            im = image.imread(str(cwd + "\coilpic.png"))
#            brain = image.imread(str(cwd + "\brain.png"))
#        
#        
#        # discards the old graph
#        self.MplWidget2.canvas.axes.clear()
#
#        self.MplWidget2.canvas.axes.imshow(
#            brain, aspect="auto", extent=(-1, 7, -4, 7), zorder=1
#        )
#
#        import itertools
#
#        r = 6
#        c = 6
#        x = np.linspace(0, c, c + 1)
#        y = np.linspace(0, r, r + 1)
#
#        pts = itertools.product(x, y)
#
#        # plot current coordinates
#        self.MplWidget2.canvas.axes.plot(
#            self.current_coil_location[0], self.current_coil_location[1], "ro", zorder=3
#        )
#        coilcoor = (
#            self.current_coil_location[0] - 0.5,
#            self.current_coil_location[0] + 2.5,
#            self.current_coil_location[1] - 4,
#            self.current_coil_location[1] + 0.4,
#        )
#        self.MplWidget2.canvas.axes.imshow(im, aspect="auto", extent=coilcoor, zorder=3)
#
#        # plot grid
#        self.MplWidget2.canvas.axes.scatter(
#            *zip(*pts), marker="o", s=30, color="blue", zorder=2
#        )
#        self.MplWidget2.canvas.axes.set_ylabel("Dorsal - Ventral")
#        self.MplWidget2.canvas.axes.set_xlabel("Anterior - Posterior")
#
#        self.MplWidget2.canvas.axes.set_xticks([])
#        self.MplWidget2.canvas.axes.set_yticks([])
#
#        textstr = str(
#            "Location: "
#            + str((self.current_coil_location[0], self.current_coil_location[1]))
#        )
#        props = dict(boxstyle="round", facecolor="wheat", alpha=1)
#
#        self.MplWidget2.canvas.axes.text(
#            0.05,
#            0.95,
#            textstr,
#            transform=self.MplWidget2.canvas.axes.transAxes,
#            fontsize=14,
#            verticalalignment="top",
#            bbox=props,
#        )
#        # refresh canvas
#        self.MplWidget2.canvas.draw()

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
    window = Ui(r"C:\Users\Ethan\Documents\GitHub\offline-inspect\merged.hdf5")
    screen = QtWidgets.QDesktopWidget().screenGeometry()
    window.resize(screen.width(), screen.height())
    window.show()
    app.exec_()
