import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType(‘visual_inspection_gui.ui’)

class VIGUI(QMainWindow):
	def __init__(self):
	super(VIGUI, self).__init__()
	self.ui = Ui_MainWindow()
	self.ui.setupUi(self)

	def stimulation_intensity_mso(self):
		self.ui.stimintensity.setText(stimulation_intensity_mso )

	def zeroxing(self):
		self.ui.zeroxinglat.setText(zcr_latency_ms)

	def peakvolts(self):
		self.ui.peakvolts.setText(pos_peak_magnitude_uv)

	def peaklatency(self):
		self.ui.peaklatency.setText(pos_peak_latency_ms)

	def troughvolts(self):
		self.ui.troughvolts.setText(neg_peak_magnitude_uv)

	def troughlatency(self):
		self.ui.troughlatency.setText(neg_peak_latency_ms)

	def event_sample(self):
		self.ui.dataindexlabel.setText(event_sample)

	def event_time(self):
		self.ui.datatimelabel.setText(event_time)

	def commentbox(self):
		self.ui.commentbox.setText(commentbox)

	def examinerlabel(self):
		self.ui.examinerlabel.setText(examinerlabel)

	def datawindow(self):
		self.ui.datawindow.setText(datawindow)

	def rejecttrial(self):
		self.ui.rejecttrial.clicked.connect()




if __name__ == ‘__main__’:
app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec_())