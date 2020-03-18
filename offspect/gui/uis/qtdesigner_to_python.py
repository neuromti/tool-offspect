# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 10:32:35 2020

@author: Ethan
"""

from PyQt5 import uic 
fin = open('visual_inspection_gui_HR.ui','r')
fout = open('visual_inspection_gui_HR.py','w')
uic.compileUi(fin,fout,execute=False)
fin.close()
fout.close()

fin = open('visual_inspection_gui_LR.ui','r')
fout = open('visual_inspection_gui_LR.py','w')
uic.compileUi(fin,fout,execute=False)
fin.close()
fout.close()