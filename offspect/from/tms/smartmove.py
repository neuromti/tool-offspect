"""
Smartmove
---------

These recordings come from the `smartmove robotic TMS <https://www.ant-neuro.com/products/smartmove>`_. This input format uses three files:

Data
****

EEG and EMG data is stored in the native file-format of the eego recording software. It can be loaded with `libeep <https://github.com/translationalneurosurgery/libeep>`_. During robotic TMS, the 64 EEG channels and the 8 EMG channels are stored in
separate :code:`.cnt` files.  

Coordinates
***********

The coordinates of the targets are stored in one or multiple :code:`targets_*.sav`-files in xml format. The filename of this save
file encodes experiment, subject pseudonym, date and hour, e.g.:
:code:`targets_<experiment>_<VvNn>_20190603_1624.sav`. These coordinates are the e.g. the grid of targets predefined before starting the mapping.

During the mapping procedure, the coordinates of the target positions, i.e. where the robot will be moved to, are saved in a :code:`documentation.txt`-file. Please note that these are the targets for the robotic movement, 
recorded, not the actual coordinates of stimulation. The actual coordinates at the time of stimulation do not appear to have been stored at all. 

Documentation of the syntax for these :code:`.txt` files will follow.

"""
