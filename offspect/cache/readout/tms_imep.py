"""
Ipsilateral MEPs induced by single pulse TMS
--------------------------------------------

This is a readout for a single channel EMG response evoked by single pulse transcranial magnetic stimulation. As this will be a single-channel-readout with a relatively clear waveform, we store only the magnitude of the first negative and positive peak and the zero-crossing latency.

"""

valid_keys = [
    "stimulation_intensity_mso",
    "stimulation_intensity_didt",
    "imep_occurence",
    "imep_latency",
    "imep_magnitude",
    "estimation_method",
    "xyz_coords",
    "channel_of_interest",
]  #: valid keys for tms-imep
