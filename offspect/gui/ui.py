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

        if filename is None:
            self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open file", "/", "CacheFiles (*.hdf5)"
            )
        else:
            self.filename = filename
        print(f"Opening {self.filename}")
        self.cf = CacheFile(self.filename)
        self.trace_idx = 0  # start with the first trace
        self.update_gui()

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

    def pull_attrs_info(self):
        attrs = self.cf.get_trace_attrs(self.trace_idx)
        print("-" * 79)
        for k, v in attrs.items():
            print(k, v)
        self.event_time_num.display(attrs["event_time"])
        self.event_id_num.display(attrs["id"])
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

    def click_next_button(self):
        if self.trace_idx == len(self.cf):
            throw_em(self, "No more traces in this direction!")
            return
        else:
            self.trace_idx += 1
            self.update_gui()

    def click_previous_button(self):
        if self.trace_idx == 0:
            throw_em(self, "No more traces in this direction!")
        else:
            self.trace_idx -= 1
            self.update_gui()

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
        pre = decode(attrs["samples_pre_event"])
        post = decode(attrs["samples_post_event"])
        fs = decode(attrs["samplingrate"])
        t0 = -float(pre) / float(fs)
        t1 = float(post) / float(fs)
        # discards the old graph
        self.MplWidget1.canvas.axes.clear()
        # plot data
        self.MplWidget1.canvas.axes.plot(data)
        self.MplWidget1.canvas.axes.set_ylim(-200, 200)
        self.MplWidget1.canvas.axes.grid(True, which="both")
        self.MplWidget1.canvas.axes.set_xticks((0, pre, pre + post))
        self.MplWidget1.canvas.axes.set_xticklabels((t0, 0, t1))
        self.MplWidget1.canvas.axes.set_xticks(
            range(0, pre + post, (pre + post) // 10), minor=True
        )
        self.MplWidget1.canvas.axes.tick_params(direction="in")
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
        from offspect.gui.uis import visual_inspection_gui as pygui

        print(f"GUI: Resolution set to default : {pygui}")
    else:
        pygui = import_module(f"offspect.gui.uis.visual_inspection_gui_{resolution}")
        print(f"GUI: Resolution set to {resolution} : {pygui}")

    class useUI(Ui, pygui.Ui_MainWindow):
        pass

    return app, useUI


def start_window(app, window):

    window.show()
    app.exec_()
