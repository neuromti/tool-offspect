File Formats
------------

Different file format will use a different number of files. Additionally,
different challenges are faced for each file-format.

.mat
****

The Matlab format is the oldest kind and mostly from recordings using lz_TMS_v4.m
or lz_TMS_v5.m (see `repository <https://github.com/translationalneurosurgery/load-tms-toolbox>`_).

The :code:`.mat` files contain a single object, and the fields of this object contain
information like channel_names, sampling_rate and raw data_traces. Therefore,
Matlab is required to load the file and recover the data. Afterwards, we can
store the data in a generic format readable by Python. An example how to script
this in Python can be found `here <https://github.com/translationalneurosurgery/stroke-tms-maps/blob/master/intens_tms/clean/_convert_mat.py>`_.

The coordinates are stored independently from the mat-file in an .xml-file
created by localite. An example how this could be implemented in Python
can be found in the `intens_tms repo <https://github.com/translationalneurosurgery/stroke-tms-maps/blob/master/intens_tms/clean/coords.py#L184>`_. The big challenge is that only the coordinates of the target/entry
pairs are saved. Yet, each target/entry pair was actually stimulated multiple
times during the recording, usually 5 times. This is not resembled in the
.xml-file. Matching can works fine, if the event count is a fixed multiple of
the coordinate counts.  Yet, if events are missing or repeated one has to
reconstruct from the labnotes or make assumptions about the correspondence
between coordinates and trigger events.


.xdf
****

This kind of file format is our preferred file format. It is `well-defined <https://github.com/sccn/xdf/wiki/Specifications>`_ and has `pxdf <https://pypi.org/project/pyxdf/>`_ to load it into Python.

As it allows to record multiple streams at once, it offers the option to record
coordinates (as e.g. sent with every pulse from localite version 4.0) together
with the raw data (as sent e.g. by eego or bvr) and additional markers.

In the optimal case, this allows easy preparation and population of the event
and trace-files. There are some files where due to errors in the recording
script or during manual recording with LabRecorder, not all streams
were recorded. In these cases, information about coordinates or other
markers might be missing. They would then have to be reconstructed manually
from the labnotes, in some cases with support from the .xml-coordinate files
stored by localite.

.cnt
****

This filetype is the native file-format of the eego recording software. It can
be loaded with `libeep <https://github.com/translationalneurosurgery/libeep>`_.
Most of our recordings would come from the robotic TMS, although a few
recordings at the start of our 2019 stroke trial would also have been recorded
as .cnt.

During robotic TMS, the 64 EEG channels and the 8 EMG channels are stored in
separate :code:`.cnt` files.  The target coordinates are stored in one or
multiple :code:`targets_*.sav`-files in xml format. The filename of this save
file encodes experiment, subject pseudonym, date and hour, e.g.:
:code:`targets_<experiment>_<VvNn>_20190603_1624.sav`. Yet, the actual
coordinates stimulated during the intervention are stored in plaintext in a
:code:`documentation.txt` file in the same folder as the :code:`.sav`-files.

Documentation of the syntax for these :code:`.txt` files will follow.

Limitations
***********

It should be noted that different to the coordinates we received in the
automated :code:`xdf`-files, the coordinates in the other formats are only
ideal assumptions. For the :code:`.mat`-files and the manual :code:`xdf`-files
with missing streams, they are read from the list of targets; for the robotic
:code:`documentation.txt`, only the targets for the robotic movement were
recorded, not the actual targets of stimulation.







