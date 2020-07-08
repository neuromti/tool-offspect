from offspect.gui.VWidgets.mpl import MplWidget
from offspect.cache.plot import plot_glass_on, get_glass_bg
from offspect.api import decode
from PyQt5.QtCore import QSize
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QPushButton, QDialog
from offspect.cache.file import CacheFile
from functools import partial


class CoordsWidget(MplWidget):
    def __init__(self, cf: CacheFile, idx: int, tmpdir, parent=None):
        MplWidget.__init__(self, parent=parent)
        self._draw(cf, idx, tmpdir)

    def _draw(self, cf: CacheFile, idx: int, tmpdir):
        tattrs = cf.get_trace_attrs(idx)
        coords = decode(tattrs["xyz_coords"])
        print(f"COORDS: Stimulation target was at {coords}")
        try:
            plot_glass_on(axes=self.canvas.axes, coords=coords, tmpdir=tmpdir)
        except Exception as e:
            InvalidCoordsDialog(cf=cf, idx=idx, message=str(e))
        self.canvas.axes.axis("off")
        self.canvas.draw()

    def sizeHint(self):
        return QSize(200, 200)


class InvalidCoordsDialog(QDialog):
    "Widget opening a dialog to correct invalid coordinates"

    def __init__(
        self,
        cf: CacheFile,
        idx: int,
        message: str = "DEFAULT:Error Description:More Information",
        *args,
        **kwargs,
    ):
        super(InvalidCoordsDialog, self).__init__(*args, **kwargs)
        self.cf = cf
        self.idx = idx
        parts = message.split(":")
        if len(parts) == 2:
            kind, msg = parts
        elif len(parts) == 3:
            kind, a, b = parts
            msg = ":".join((a, b))
        else:
            raise Exception(f"{message} has to many parts")

        print(message)
        prv = QPushButton(text="Replace with previous")
        prv.clicked.connect(partial(self.replace, which=idx - 1))
        ign = QPushButton(text="Ignore")
        ign.clicked.connect(self.close)
        nxt = QPushButton(text="Replace with next")
        nxt.clicked.connect(partial(self.replace, which=idx + 1))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel(text="\n".join(message.split(":"))))
        buttons = QtWidgets.QHBoxLayout()
        for w in [prv, ign, nxt]:
            buttons.addWidget(w)
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.setWindowTitle(kind + " Error")
        self.exec_()

    def replace(self, which: int):
        trace_num = len(self.cf)
        if which == self.idx or which < 0 or which > trace_num:
            pass
        else:
            new_attrs = self.cf.get_trace_attrs(which)
            tattrs = self.cf.get_trace_attrs(self.idx)
            tattrs["xyz_coords"] = new_attrs["xyz_coords"]
            self.cf.set_trace_attrs(self.idx, tattrs)
        self.close()
