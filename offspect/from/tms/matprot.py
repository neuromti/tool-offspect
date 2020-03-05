"""
Matlab Protocol
---------------

The Matlab format is the oldest kind and mostly from recordings using lz_TMS_v4.m
or lz_TMS_v5.m (see `repository <https://github.com/translationalneurosurgery/load-tms-toolbox>`_). It is based on two files.

- :code:`.mat`
- :code:`.xml`

Data
****

The :code:`.mat` files contain a single Matlab object. The fields of this object contain the raw EEG and EMG data, and information like channel_names, sampling_rate and raw data_traces. Because it is a Matlab object, it is necessary to load the file with Matlab to recover the data. Afterwards, we can
store the data in a generic format readable by Python. An example how to script
this in Python can be found `here <https://github.com/translationalneurosurgery/stroke-tms-maps/blob/master/intens_tms/clean/_convert_mat.py>`_.

Coordinates
***********

By design, the coordinates of the target-entry pairs were stored  independently from the :code:`mat`-file in an :code:`xml`-file created by localite.  The pairing of coordinates with a specific trace needs to be reconstructed manually (see :ref:`support-link-coords`).  

"""
