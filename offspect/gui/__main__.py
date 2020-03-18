""" 
"""
from PyQt5 import QtWidgets
from offspect.gui import visual_inspection_gui_HR as pygui
import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from offspect.api import CacheFile
from offspect.gui.plot import plot_m1s

# Ensure using PyQt5 backend
matplotlib.use("QT5Agg")
matplotlib.rcParams["axes.linewidth"] = 0.1

def throw_em(parent, message: str):
    em = QtWidgets.QErrorMessage(parent=parent)
    em.showMessage(message)

class Ui(QtWidgets.QMainWindow, pygui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Ui, self).__init__(parent)
        self.setupUi(self)
        self.addToolBar(NavigationToolbar(self.MplWidget1.canvas, self))

        self.reject_button.setCheckable(True)
        self.reject_button.clicked.connect(self.flip_reject_button)
        self.previous_button.clicked.connect(self.update_previous_button)
        self.next_button.clicked.connect(self.update_next_button)
        self.update_attrs_button.clicked.connect(self.update_attributes)

        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file", "/", "CacheFiles (*.hdf5)")

        print(self.filename)
        self.cf = CacheFile(self.filename)
        self.trace_idx = 0  # start with the first trace
        self.get_trace_from_cache()
        self.plot_mep()
        self.pull_attrs_info()
        self.attrs = self.cf.get_trace_attrs(self.trace_idx)
        self.initialize_reject_button()
        self.plot_coil_coordinates()

    def update_attributes(self):
                
        self.attrs['neg_peak_magnitude_uv']      = self.troughmag_num.text()
        self.attrs['neg_peak_latency_ms']        = self.troughlat_num.text()
        self.attrs['pos_peak_latency_ms']        = self.peaklat_num.text()
        self.attrs['pos_peak_magnitude_uv']      = self.peakmag_num.text()
        self.attrs['zcr_latency_ms']             = self.zcr_lat_num.text()
        self.attrs['stimulation_intensity_mso']  = self.stimintensity_num.text()
        self.attrs['time_since_last_pulse_in_s'] = self.time_since_pulse_num.text()
        self.attrs['stimulation_intensity_didt'] = self.didt_num.text()
        self.attrs['comment']                    = self.commentbox.toPlainText()
        self.attrs["reject"]                     = self.reject
        
        self.cf.set_trace_attrs(self.trace_idx, self.attrs)

    def initialize_reject_button(self):
        if self.attrs["reject"] == True:
            self.reject = True
            self.reject_button.setStyleSheet("background-color: red")
        elif self.attrs["reject"] == False:
            self.reject = False
            self.reject_button.setStyleSheet("background-color: light gray")

    def flip_reject_button(self):

        if self.attrs["reject"] == False:
            self.reject_button.setStyleSheet("background-color: red")
            self.attrs["reject"] = True
            self.reject = True
        elif self.attrs["reject"] == True:
            self.reject_button.setStyleSheet("background-color: light gray")
            self.attrs['reject'] = False
            self.reject = False
        
    def pull_attrs_info(self):
        self.attrs = self.cf.get_trace_attrs(self.trace_idx)
                
        self.event_time_num.display(self.attrs["event_time"])
        self.event_id_num.display(self.attrs["id"])
        self.troughmag_num.setText(self.attrs["neg_peak_magnitude_uv"])
        self.troughlat_num.setText(self.attrs["neg_peak_latency_ms"])
        self.peaklat_num.setText(self.attrs["pos_peak_latency_ms"])
        self.peakmag_num.setText(self.attrs["pos_peak_magnitude_uv"])
        self.zcr_lat_num.setText(self.attrs["zcr_latency_ms"])
        self.stimintensity_num.setText(self.attrs["stimulation_intensity_mso"])
        self.time_since_pulse_num.setText(self.attrs["time_since_last_pulse_in_s"])
        self.didt_num.setText(self.attrs["stimulation_intensity_didt"])

        self.channel_label.setText(self.attrs["channel_labels"][0])
        self.filename_label_2.setText(self.attrs["original_file"])
        self.examiner_name.setText(self.attrs["examiner"])
        self.readout.setText(self.attrs["readout"])

        self.commentbox.setText(self.attrs["comment"])
        
        self.xyz_coords = self.attrs['xyz_coords']
        self.coil_coordinate_input.setText(self.xyz_coords)

    def update_next_button(self):
        try:
            self.trace_idx += 1
            self.get_trace_from_cache()
            self.plot_mep()
            self.pull_attrs_info()
            self.reject_button.setCheckable(True)
            self.initialize_reject_button()
            self.plot_coil_coordinates()
        except Exception as e:
            throw_em(self, str(e))            

    def update_previous_button(self):
        try:
            self.trace_idx -= 1
            self.get_trace_from_cache()
            self.plot_mep()
            self.pull_attrs_info()
            self.reject_button.setCheckable(True)
            self.initialize_reject_button()
            self.plot_coil_coordinates()
        except Exception as e:
            throw_em(self, str(e))

    def get_trace_from_cache(self):
        self.trace = self.cf.get_trace_data(self.trace_idx)

    def plot_mep(self):
        data = self.trace
        # discards the old graph
        self.MplWidget1.canvas.axes.clear()
        # plot data
        self.MplWidget1.canvas.axes.plot(data)
        # refresh canvas
        self.MplWidget1.canvas.draw()

    def plot_coil_coordinates(self):
        
        if self.attrs['channel_labels'][0][4] == 'L':
            rM1 = self.xyz_coords
            coords = [rM1]
            values = [float(self.attrs['pos_peak_magnitude_uv']) + abs(float(self.attrs['neg_peak_magnitude_uv']))]
        else:
            lM1 = self.xyz_coords
            coords = [lM1]
            values = [float(self.attrs['pos_peak_magnitude_uv']) + abs(float(self.attrs['neg_peak_magnitude_uv']))]
        display = plot_m1s(coords = coords, values = values)
        display.savefig('pretty_brain.png')  
        display.close()
        
        self.MplWidget2.canvas.axes.clear()
        im = matplotlib.pyplot.imread('pretty_brain.png')

        self.MplWidget2.canvas.axes.imshow(im)
        self.MplWidget2.canvas.axes.axis('off')
        # refresh canvas
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
            app.exit()
        else:
            event.ignore()

#%%
        
            
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    app.exec_()
