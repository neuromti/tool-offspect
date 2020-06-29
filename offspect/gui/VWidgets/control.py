from PyQt5 import QtWidgets, QtCore
from offspect.api import CacheFile, decode, encode
from typing import Callable
from functools import partial
from offspect.cache.attrs import get_valid_trace_keys
from .textedit import VTextEdit
from offspect.gui.io import save
from offspect.cache.file import write_tracedata
from offspect.cache.steps import process_data
import numpy as np
from datetime import datetime


class IntegerAttribute(QtWidgets.QWidget):
    def read(self):
        text = self.line.text()
        try:
            text = str(int(text))
        except Exception:
            text = "0"
            self.line.setText(text)

        return str(text)

    def on_edit(self):
        save(cf=self.cf, idx=self.idx, key=self.key, read=self.read)
        self.callback()

    def draw_int(self, idx: int = 0):
        self.idx = idx
        tattr = self.cf.get_trace_attrs(self.idx)
        val = decode(tattr[self.key])
        val = val or 0
        if type(val) == str:
            val = 0
        elif type(val) == float:
            val = int(val)
        val = "{0:3.0f}".format(val)
        print(f"TATTR: Loading {self.key}:{val} for {idx}")
        self.line.setText(val)

    def __init__(
        self,
        cf: CacheFile,
        idx: int = 0,
        key: str = "onset_shift",
        callback: Callable = lambda: None,
        parent=None,
    ):
        super().__init__()
        self.key = key
        self.cf = cf
        self.idx = idx
        self.callback = callback
        self.label = QtWidgets.QLabel(text=key.replace("_", " ").capitalize())
        self.line = QtWidgets.QLineEdit()
        self.draw_int(idx)
        self.line.returnPressed.connect(self.on_edit)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line)

        self.setLayout(layout)


class ControlWidget(QtWidgets.QWidget):
    def __init__(self, cf=None, idx: int = 1, callback=lambda: None, *args, **kwargs):
        super(ControlWidget, self).__init__(*args, **kwargs)
        self.callback = callback
        self.cf = cf

        # Navigation Line
        self.navigationlayout = QtWidgets.QHBoxLayout()
        self.trace_count = QtWidgets.QLabel(f" of {len(self.cf)}")
        self.next_button = QtWidgets.QPushButton(text="Next")
        self.prev_button = QtWidgets.QPushButton(text="Prev")
        self.reject_button = QtWidgets.QPushButton(text="Reject")
        self.trace_idx_num = QtWidgets.QLineEdit(text=str(idx))
        self.trace_idx_num.returnPressed.connect(self.switch_trace)
        self.reject_button.clicked.connect(self.flip_reject_button)
        self.prev_button.clicked.connect(self.click_prev)
        self.next_button.clicked.connect(self.click_next)
        for button in [
            self.prev_button,
            self.trace_idx_num,
            self.trace_count,
            self.next_button,
        ]:
            self.navigationlayout.addWidget(button)

        # Rejection Line
        self.rejectionlayout = QtWidgets.QHBoxLayout()
        for item in [self.reject_button]:
            self.rejectionlayout.addWidget(item)

        # Onset Shift
        self.onsetlayout = QtWidgets.QHBoxLayout()
        self.onset_shift = IntegerAttribute(
            cf=self.cf, idx=self.trace_idx, key="onset_shift", callback=self.refresh
        )
        for item in [self.onset_shift]:
            self.onsetlayout.addWidget(item)

        self.manipulatelayout = QtWidgets.QHBoxLayout()
        self.baseline_button = QtWidgets.QPushButton(text="Baseline")
        self.baseline_button.clicked.connect(self.click_baseline)
        self.detrend_button = QtWidgets.QPushButton(text="Detrend")
        self.detrend_button.clicked.connect(self.click_detrend)
        self.linenoise_button = QtWidgets.QPushButton(text="LineNoise")
        self.linenoise_button.clicked.connect(self.click_linenoise)
        self.flip_sign_button = QtWidgets.QPushButton(text="Flip Signal")
        self.flip_sign_button.clicked.connect(self.click_flipsign)
        self.undo_button = QtWidgets.QPushButton(text="Undo")
        self.undo_button.clicked.connect(self.click_undo)

        for item in [
            self.baseline_button,
            self.detrend_button,
            self.linenoise_button,
            self.flip_sign_button,
            self.undo_button,
        ]:
            self.manipulatelayout.addWidget(item)

        self.estimatelayout = QtWidgets.QHBoxLayout()
        self.estimate_button = QtWidgets.QPushButton(
            text="Estimate Amplitude and Latency"
        )
        self.estimate_button.clicked.connect(self.click_estimate_parameters)
        self.estimate_amp_button = QtWidgets.QPushButton(text="Amplitude from Latency")
        self.estimate_amp_button.clicked.connect(self.click_estimate_amplitudes)
        self.hasmep_button = QtWidgets.QPushButton(text="MEP positive")
        self.hasmep_button.clicked.connect(self.click_hasmep)
        for item in [
            self.estimate_button,
            self.hasmep_button,
            self.estimate_amp_button,
        ]:
            self.estimatelayout.addWidget(item)

        # Vertical Spaces
        verticalSpacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.navigationlayout)
        layout.addLayout(self.rejectionlayout)
        layout.addLayout(self.onsetlayout)
        layout.addLayout(self.manipulatelayout)
        layout.addLayout(self.estimatelayout)
        layout.addItem(verticalSpacer)
        self.setLayout(layout)
        self.trace_idx = idx

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
            self.prev_button.setEnabled(True)
        elif trace_idx <= 1:
            trace_idx = 1
            self.next_button.setEnabled(True)
            self.prev_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)
        print("CTRL: Setting trace_idx from", self.trace_idx + 1, "to", trace_idx)
        self.trace_idx_num.setText(str(trace_idx))
        self.refresh()

    def click_next(self):
        self.trace_idx += 1

    def click_prev(self):
        self.trace_idx -= 1

    def switch_trace(self):
        print("CTRL: Switching trace_idx manually to", self.trace_idx + 1)
        self.refresh()

    def refresh(self):
        self.onset_shift.draw_int(self.trace_idx)
        self.draw_reject_button()
        self.draw_hasmep_button()
        self.callback()

    def draw_reject_button(self):
        tattrs = self.cf.get_trace_attrs(self.trace_idx)
        reject = decode(tattrs["reject"])
        reject = False if reject is None else reject
        self.cf.set_trace_attrs(self.trace_idx, tattrs)
        if reject:
            self.reject_button.setStyleSheet("background-color: red")
            self.reject_button.setText("Rejected")
        else:
            self.reject_button.setStyleSheet("background-color: green")
            self.reject_button.setText("Accepted")

    def flip_reject_button(self):
        tattrs = self.cf.get_trace_attrs(self.trace_idx)
        reject = decode(tattrs["reject"])
        reject = True if reject is None else not reject
        tattrs["reject"] = reject
        self.cf.set_trace_attrs(self.trace_idx, tattrs)
        self.draw_reject_button()

    def draw_hasmep_button(self):
        tattrs = self.cf.get_trace_attrs(self.trace_idx)
        pamp = decode(tattrs["pos_peak_magnitude_uv"]) or 0
        namp = decode(tattrs["neg_peak_magnitude_uv"]) or 0
        ptp = pamp - namp
        if ptp != 0:
            self.hasmep_button.setStyleSheet("background-color: green")
            self.hasmep_button.setText("MEP positive")
        else:
            self.hasmep_button.setStyleSheet("background-color: red")
            self.hasmep_button.setText("MEP negative")

    def click_hasmep(self):
        print(self.hasmep_button.text())
        if self.hasmep_button.text() == "MEP positive":
            tattrs = self.cf.get_trace_attrs(self.trace_idx)
            tattrs["neg_peak_latency_ms"] = encode(0)
            tattrs["pos_peak_latency_ms"] = encode(0)
            tattrs["neg_peak_magnitude_uv"] = encode(0)
            tattrs["pos_peak_magnitude_uv"] = encode(0)
            self.cf.set_trace_attrs(self.trace_idx, tattrs)
            self.draw_hasmep_button()
            self.callback()

    def log(self, event: str, idx: int):
        attrs = self.cf.get_trace_attrs(idx)
        if "_log" in attrs.keys():
            log = decode(attrs["_log"])
        else:
            log = []
        happening = str(event) + " on " + str(datetime.now())
        print("Logging", happening, "to", log)
        log.append(happening)
        attrs["_log"] = encode(log)
        self.cf.set_trace_attrs(self.trace_idx, attrs)

    def undo(self, idx):
        attrs = self.cf.get_trace_attrs(idx)
        if "_log" in attrs.keys():
            log = decode(attrs["_log"])
        else:
            log = []

        if len(log) > 0:
            event = log.pop()
            step, when = event.split(" on ")
            print("Undoing", step, "from", when)
        else:
            print("Nothing to undo")
        attrs["_log"] = encode(log)
        self.cf.set_trace_attrs(self.trace_idx, attrs)

    def click_undo(self):
        idx = self.trace_idx
        self.undo(idx)
        self.callback()

    def click_baseline(self):
        idx = self.trace_idx
        self.log("baseline", idx)
        # data = self.cf.get_trace_data(idx)
        # attrs = self.cf.get_trace_attrs(idx)
        # pre = decode(attrs["samples_pre_event"])
        # shift = decode(attrs["onset_shift"]) or 0
        # bl = data[: pre + shift].mean(0)
        # data = data - bl
        # write_tracedata(self.cf, data, idx)
        # print(f"Performed baseline correction with {float(bl):3.2f}")
        self.callback()

    def click_detrend(self):
        idx = self.trace_idx
        self.log("detrend", idx)
        # data = self.cf.get_trace_data(idx)
        # slope = np.mean(np.diff(data), 0)
        # correction = np.arange(0, len(data)) * slope
        # data = data - correction
        # write_tracedata(self.cf, data, idx)
        # print(f"Performed detrend correction with {float(slope):3.2f}")
        self.callback()

    def click_linenoise(self):
        idx = self.trace_idx
        self.log("linenoise", idx)
        # data = self.cf.get_trace_data(idx)
        # signal = data.copy()
        # attrs = self.cf.get_trace_attrs(idx)
        # fs = decode(attrs["samplingrate"])
        # timestep = 1 / fs
        # original_len = len(signal)
        # filter_order = 100
        # while len(signal) < fs:
        #     signal = np.pad(signal, (1, 0), "constant", constant_values=(0))
        # fourier = np.fft.fft(signal)
        # freq = np.fft.fftfreq(len(signal), d=timestep)
        # fidx = int(np.where(freq == 50)[0][0])
        # fourier[fidx] = 0
        # signal = np.fft.ifft(fourier)
        # signal = signal[-original_len:]
        # data[:] = signal
        # write_tracedata(self.cf, data, idx)
        # print(f"Performed linenoise filtering")
        self.callback()

    def click_flipsign(self):
        idx = self.trace_idx
        self.log("flipsign", idx)
        # data = self.cf.get_trace_data(idx)
        # print(f"Flipping sign of trace")
        # write_tracedata(self.cf, -data, idx)
        self.callback()

    def click_estimate_parameters(self):
        window = (15, 120)
        idx = self.trace_idx
        data = self.cf.get_trace_data(idx)
        tattrs = self.cf.get_trace_attrs(idx)
        data = process_data(data, tattrs, key="_log")

        pre = decode(tattrs["samples_pre_event"])
        shift = decode(tattrs["onset_shift"]) or 0
        fs = decode(tattrs["samplingrate"])
        onset = pre - shift
        print(shift, fs)
        minlat = int(window[0] * fs / 1000)
        maxlat = int(window[1] * fs / 1000)
        a = onset + minlat
        b = onset + maxlat
        mep = data[a:b]
        nlat = mep.argmin()
        plat = mep.argmax()
        namp = float(mep[nlat])
        pamp = float(mep[plat])
        nlat = mep.argmin() * 1000 / fs
        plat = mep.argmax() * 1000 / fs
        print("Estimating latencies to be", nlat, plat)
        print("Estimating amplitudes to be", namp, pamp)
        tattrs["neg_peak_latency_ms"] = encode(float(nlat + window[0]))
        tattrs["neg_peak_magnitude_uv"] = encode(namp)
        tattrs["pos_peak_latency_ms"] = encode(float(plat + window[0]))
        tattrs["pos_peak_magnitude_uv"] = encode(pamp)
        self.cf.set_trace_attrs(idx, tattrs)
        self.draw_hasmep_button()
        self.callback()

    def click_estimate_amplitudes(self):
        idx = self.trace_idx
        data = self.cf.get_trace_data(idx)
        tattrs = self.cf.get_trace_attrs(idx)
        data = process_data(data, tattrs, key="_log")

        fs = decode(tattrs["samplingrate"])
        nlat = int((decode(tattrs["neg_peak_latency_ms"]) or 0) * fs / 1000)
        plat = int((decode(tattrs["pos_peak_latency_ms"]) or 0) * fs / 1000)
        # MEP negative trials
        if nlat == plat:
            print("MEP negative or identical latencies", nlat, plat)
            tattrs["neg_peak_latency_ms"] = encode(0)
            tattrs["pos_peak_latency_ms"] = encode(0)
            tattrs["neg_peak_magnitude_uv"] = encode(0)
            tattrs["pos_peak_magnitude_uv"] = encode(0)
        else:
            pre = decode(tattrs["samples_pre_event"])
            shift = decode(tattrs["onset_shift"]) or 0
            namp = float(data[nlat + pre + shift])
            pamp = float(data[plat + pre + shift])
            print("Estimating amplitudes to be", namp, pamp)
            tattrs["neg_peak_magnitude_uv"] = encode(namp)
            tattrs["pos_peak_magnitude_uv"] = encode(pamp)

        self.cf.set_trace_attrs(idx, tattrs)
        self.draw_hasmep_button()
        self.callback()
