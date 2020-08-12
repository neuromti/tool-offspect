"""
Contralateral MEPs induced by single pulse TMS
----------------------------------------------

This is a readout for a single channel EMG response evoked by single pulse transcranial magnetic stimulation. As this will be a single-channel-readout with a relatively clear waveform, we store only the magnitude of the first negative and positive peak and the zero-crossing latency.

"""
valid_keys = [
    "stimulation_intensity_mso",
    "stimulation_intensity_didt",
    "neg_peak_magnitude_uv",
    "neg_peak_latency_ms",
    "pos_peak_magnitude_uv",
    "pos_peak_latency_ms",
    "zcr_latency_ms",
    "xyz_coords",
    "channel_of_interest",
    "measured_phase",
    "target_phase",
]  #: valid keys for tms-cmep (formerly know as 'contralateral-mep')
