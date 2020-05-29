from offspect.gui.VWidgets.mpl import MplWidget
from .plot import plot_glass_on, get_glass_bg
from offspect.api import decode
from PyQt5.QtCore import QSize


class CoordsWidget(MplWidget):
    def __init__(self, cf, idx, tmpdir, parent=None):
        MplWidget.__init__(self, parent=parent)
        tattrs = cf.get_trace_attrs(idx)
        coords = decode(tattrs["xyz_coords"])
        self._draw(coords, tmpdir)

    def _draw(self, coords, tmpdir):
        print(f"GUI: Stimulation target was at {coords}")
        plot_glass_on(axes=self.canvas.axes, coords=coords, tmpdir=tmpdir)
        self.canvas.axes.axis("off")
        self.canvas.draw()

    def sizeHint(self):
        return QSize(200, 200)
