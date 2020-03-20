# -*- coding: utf-8 -*-
"""
In Designer, promote a default QWidget to MplWidget, with the header file being the path of this file relative to the .ui file, e.g. `.mplwidget.py`.

Alternatively, compile each  ui-file with e.g :code:`pyuic5 visual_inspection_gui_<RESOLUTION>.ui > visual_inspection_gui_<RESOLUTION>.py` and you can use with this ui with the visual inspection GUI
"""

from PyQt5 import uic
from pathlib import Path

uis = Path(__file__).parent.glob("*.ui")

for ui in uis:
    with ui.open("r") as fin:
        with ui.with_suffix(".py").open("w") as fout:
            uic.compileUi(fin, fout, execute=False)

# with open("visual_inspection_gui_HR.ui", "r") as fin:
#     with open("visual_inspection_gui_HR.py", "w") as fout:
#         uic.compileUi(fin, fout, execute=False)


# with open("visual_inspection_gui_LR.ui", "r") as fin:
#     with open("visual_inspection_gui_LR.py", "w") as fout:
#         uic.compileUi(fin, fout, execute=False)
