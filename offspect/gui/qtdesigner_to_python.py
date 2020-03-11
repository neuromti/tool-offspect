# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 10:32:35 2020

@author: Ethan
"""

from PyQt5 import uic 
fin = open('visual_inspection_gui.ui','r')
fout = open('visual_inspection_gui.py','w')
uic.compileUi(fin,fout,execute=False)
fin.close()
fout.close()