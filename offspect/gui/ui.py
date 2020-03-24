from importlib import import_module
from PyQt5 import QtWidgets
from tempfile import TemporaryDirectory
from pathlib import Path
import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from offspect.api import CacheFile
from offspect.gui.plot import plot_glass_on
from offspect.api import decode, encode
import numpy as np

# Ensure using PyQt5 backend
matplotlib.use("QT5Agg")
matplotlib.rcParams["axes.linewidth"] = 0.1


def throw_em(parent, message: str):
    em = QtWidgets.QErrorMessage(parent=parent)
    em.showMessage(message)


class Ui(QtWidgets.QMainWindow):
    def __init__(self, parent=None, filename=None):
        super(Ui, self).__init__(parent)
        self.setupUi(self)
        self.addToolBar(NavigationToolbar(self.MplWidget1.canvas, self))

        self.reject_button.clicked.connect(self.flip_reject_button)
        self.previous_button.clicked.connect(self.click_previous_button)
        self.next_button.clicked.connect(self.click_next_button)
        self.update_attrs_button.clicked.connect(self.save_attributes)
        # self.trace_update_button.clicked.connect(self.random_access_trace)
        self.trace_idx_num.editingFinished.connect(self.check_trace_idx)
        if filename is None:
            self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open file", "/", "CacheFiles (*.hdf5)"
            )
        else:
            self.filename = filename
        print(f"Opening {self.filename}")
        self.cf = CacheFile(self.filename)
        # start with the first trace

        # get the index of the last trace in hdf5 file
        self.last_trace_num.display(len(self.cf))
        self.trace_idx = 0  # updates the gui
        # self.update_gui()

    def save_attributes(self):
        attrs = self.cf.get_trace_attrs(self.trace_idx)
        attrs["neg_peak_magnitude_uv"] = self.troughmag_num.text()
        attrs["neg_peak_latency_ms"] = self.troughlat_num.text()
        attrs["pos_peak_latency_ms"] = self.peaklat_num.text()
        attrs["pos_peak_magnitude_uv"] = self.peakmag_num.text()
        attrs["zcr_latency_ms"] = self.zcr_lat_num.text()
        attrs["stimulation_intensity_mso"] = self.stimintensity_num.text()
        attrs["time_since_last_pulse_in_s"] = self.time_since_pulse_num.text()
        attrs["stimulation_intensity_didt"] = self.didt_num.text()
        attrs["comment"] = self.commentbox.toPlainText()
        attrs["reject"] = self.reject
        attrs["xyz_coords"] = self.coil_coordinate_input.text()
        self.cf.set_trace_attrs(self.trace_idx, attrs)
        self.update_gui()

    def initialize_reject_button(self):
        self.reject_button.setCheckable(self.reject)
        if self.reject:
            self.reject_button.setStyleSheet("background-color: red")
        else:
            self.reject_button.setStyleSheet("background-color: green")

    def flip_reject_button(self):
        self.reject = not self.reject
        self.initialize_reject_button()
        # save the rejection when the button is pressed
        self.save_attributes()
        self.update_gui()

    def pull_attrs_info(self):
        attrs = self.cf.get_trace_attrs(self.trace_idx)
        print("-" * 79)
        for k, v in attrs.items():
            print(k, v)
        self.event_time_num.display(attrs["event_time"])
        # self.trace_idx_num.setText(attrs["id"])
        # this was the id within a source file, not the running continous index
        # within a merged file, it is now the index

        self.troughmag_num.setText(attrs["neg_peak_magnitude_uv"])
        self.troughlat_num.setText(attrs["neg_peak_latency_ms"])
        self.peaklat_num.setText(attrs["pos_peak_latency_ms"])
        self.peakmag_num.setText(attrs["pos_peak_magnitude_uv"])
        self.zcr_lat_num.setText(attrs["zcr_latency_ms"])
        self.stimintensity_num.setText(attrs["stimulation_intensity_mso"])
        self.time_since_pulse_num.setText(attrs["time_since_last_pulse_in_s"])
        self.didt_num.setText(attrs["stimulation_intensity_didt"])
        self.channel_label.setText(attrs["channel_labels"][0])
        self.filename_label_2.setText(attrs["origin"])
        self.examiner_name.setText(attrs["examiner"])
        self.readout.setText(attrs["readout"])
        self.commentbox.setText(attrs["comment"])
        self.xyz_coords = attrs["xyz_coords"]
        self.coil_coordinate_input.setText(self.xyz_coords)
        self.reject = decode(attrs["reject"])

        # calculate VPP to be displayed in the plot
        self.vpp = abs(float(attrs["neg_peak_magnitude_uv"])) + float(
            attrs["pos_peak_magnitude_uv"]
        )

    @property
    def trace_idx(self):
        try:
            trace_idx = int(float(self.trace_idx_num.text())) - 1
        except ValueError:
            trace_idx = 0
        trace_idx = max((trace_idx, 0))
        trace_idx = min((trace_idx, len(self.cf) - 1))
        return trace_idx  # correct for the display starting counting at 1, not zero

    @trace_idx.setter
    def trace_idx(self, trace_idx: int):
        trace_idx += 1  # add one to start displaying at 1, not zero
        maxidx = len(self.cf)
        if trace_idx >= maxidx:
            trace_idx = maxidx
            self.next_button.setEnabled(False)
            self.previous_button.setEnabled(True)
        elif trace_idx <= 1:
            trace_idx = 1
            self.next_button.setEnabled(True)
            self.previous_button.setEnabled(False)
        else:
            self.previous_button.setEnabled(True)
            self.next_button.setEnabled(True)

        print("Setting trace_idx from", self.trace_idx, "to", trace_idx)
        self.trace_idx_num.setText(str(trace_idx))
        self.update_gui()

    def check_trace_idx(self):
        self.trace_idx += 0

    def click_next_button(self):
        self.trace_idx += 1

    def click_previous_button(self):
        self.trace_idx -= 1

    def update_gui(self):
        try:
            self.pull_attrs_info()
            self.plot_trace()
            self.plot_coords()
            self.initialize_reject_button()
        except Exception as e:
            print("Exception", e)
            throw_em(self, str(e))

    def plot_trace(self):

        data = self.cf.get_trace_data(self.trace_idx)
        attrs = self.cf.get_trace_attrs(self.trace_idx)
        # probably better to put the rest of this into a function in a
        # different file and then import the function
        # function could hat the signature
        # plot_trace(ax, data, attrs) and be called e.g. like
        # plot_trace(self.MplWidget1.canvas.axes, data, attrs)
        # this allows to work an separate plotting functions for different
        # readouts and prevent merging conflicts within this base class.

        # everything into a function from here on
        pre = decode(attrs["samples_pre_event"])
        post = decode(attrs["samples_post_event"])
        fs = decode(attrs["samplingrate"])
        t0 = -float(pre) / float(fs)
        t1 = float(post) / float(fs)
        # get indices of tms pulse
        peak = np.where(data == np.max(data))[0][0]
        trough = np.where(data == np.min(data))[0][0]
        if peak > trough:
            latest = peak
        else:
            latest = trough
        # find MEP
        mep_peak = np.where(data == np.max(data[latest + 5 :]))[0][0]
        mep_trough = np.where(data == np.min(data[latest + 5 :]))[0][0]
        timey = np.arange(0, len(data), 1)

        textstr = "Vpp = {0:3.2f}".format(self.vpp)
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

        # discards the old graph
        self.MplWidget1.canvas.axes.clear()
        self.MplWidget1.canvas.axes.text(
            0.05,
            0.95,
            textstr,
            transform=self.MplWidget1.canvas.axes.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props,
        )
        # plot data
        self.MplWidget1.canvas.axes.plot(timey, data)
        self.MplWidget1.canvas.axes.vlines(
            timey[mep_peak], data[mep_peak], 0, color="red", linestyle="dashed"
        )
        self.MplWidget1.canvas.axes.vlines(
            timey[mep_trough], data[mep_trough], 0, color="red", linestyle="dashed"
        )
        self.MplWidget1.canvas.axes.set_ylim(-200, 200)
        self.MplWidget1.canvas.axes.grid(True, which="both")
        self.MplWidget1.canvas.axes.set_xticks((0, pre, pre + post))
        self.MplWidget1.canvas.axes.set_xticklabels((t0, 0, t1))
        self.MplWidget1.canvas.axes.set_xticks(
            range(0, pre + post, (pre + post) // 10), minor=True
        )
        self.MplWidget1.canvas.axes.tick_params(direction="in")

        # everything into a function until here
        # refresh canvas
        self.MplWidget1.canvas.draw()

    def plot_coords(self):
        coords = decode(self.cf.get_trace_attrs(self.trace_idx)["xyz_coords"])

        print(f"Plotting {coords}")
        plot_glass_on(self.MplWidget2.canvas.axes, [coords], [1000.0])
        self.MplWidget2.canvas.axes.axis("off")
        self.MplWidget2.canvas.draw()

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Message",
            "Are you sure to quit?",
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.close()
        else:
            event.ignore()


def get_ui(resolution: str = ""):
    app = QtWidgets.QApplication([__file__])
    if resolution == "":
        resolution = "HR"
        print(f"GUI: Resolution not specified. Fall back to default")

    pygui = import_module(f"offspect.gui.uis.visual_inspection_gui_{resolution}")
    print(f"GUI: Using {resolution}: {pygui.__name__}")

    class useUI(Ui, pygui.Ui_MainWindow):  # type: ignore
        pass

    return app, useUI


def start_window(app, window):

    window.show()
    app.exec_()
