from offspect.gui.VWidgets.mpl import MplWidget
from offspect.cache.plot import plot_glass_on, get_glass_bg
from offspect.api import decode
from PyQt5.QtCore import QSize
from offspect.gui.VWidgets.message import raise_error


class CoordsWidget(MplWidget):
    def __init__(self, cf, idx, tmpdir, parent=None):
        MplWidget.__init__(self, parent=parent)
        tattrs = cf.get_trace_attrs(idx)
        coords = decode(tattrs["xyz_coords"])
        self._draw(coords, tmpdir)

    def _draw(self, coords, tmpdir):
        print(f"GUI: Stimulation target was at {coords}")
        try:
            plot_glass_on(axes=self.canvas.axes, coords=coords, tmpdir=tmpdir)
        except Exception as e:
            raise_error(str(e))
        self.canvas.axes.axis("off")
        self.canvas.draw()

    def sizeHint(self):
        return QSize(200, 200)
