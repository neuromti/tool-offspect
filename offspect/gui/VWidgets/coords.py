from offspect.gui.VWidgets.mpl import MplWidget
from offspect.gui.plot import plot_glass_on
from offspect.api import decode
from PyQt5.QtCore import QSize


class CoordsWidget(MplWidget):
    def __init__(self, cf, idx, parent=None):
        MplWidget.__init__(self, parent=parent)
        tattrs = cf.get_trace_attrs(idx)
        coords = decode(tattrs["xyz_coords"])
        self._draw(coords)

    def _draw(self, coords, values=[1000.0]):
        print(f"GUI: Stimulation target was at {coords}")
        plot_glass_on(self.canvas.axes, [coords], values)
        print(f"GUI: Stimulation was at {coords}")
        self.canvas.axes.axis("off")
        self.canvas.draw()

    def sizeHint(self):
        return QSize(200, 200)
