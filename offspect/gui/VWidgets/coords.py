from offspect.gui.VWidgets.mpl import MplWidget
from offspect.gui.VWidgets.message import raise_error
from offspect.cache.plot import plot_glass_on, get_glass_bg
from offspect.api import decode
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMessageBox
from offspect.cache.file import CacheFile


class CoordsWidget(MplWidget):
    def __init__(self, cf: CacheFile, idx: int, tmpdir, parent=None):
        MplWidget.__init__(self, parent=parent)
        self._draw(cf, idx, tmpdir)

    def _draw(self, cf: CacheFile, idx: int, tmpdir):
        tattrs = cf.get_trace_attrs(idx)
        coords = decode(tattrs["xyz_coords"])
        print(f"GUI: Stimulation target was at {coords}")
        try:
            plot_glass_on(axes=self.canvas.axes, coords=coords, tmpdir=tmpdir)
        except Exception as e:
            InvalidCoordsDialog(cf=cf, idx=idx, message=str(e))
        self.canvas.axes.axis("off")
        self.canvas.draw()

    def sizeHint(self):
        return QSize(200, 200)


class InvalidCoordsDialog(QMessageBox):
    """Widget listing all Origin Attributes
        

    Example::

        python -m offspect.gui.baseui stroke_map.hdf5  0
        python -m offspect.gui.baseui stroke_mep.hdf5  0
    """

    def __init__(
        self,
        cf: CacheFile,
        idx: int,
        message: str = "DEFAULT:Error Description:More Information",
        *args,
        **kwargs,
    ):
        super(InvalidCoordsDialog, self).__init__(*args, **kwargs)
        kind, msg, info = message.split(":")
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(kind + " Error")
        self.setText(msg)
        self.setInformativeText(info)
        self.exec_()
