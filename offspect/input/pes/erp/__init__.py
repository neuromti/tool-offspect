"""
ERPs induced by single pulse PES
--------------------------------

This is a readout for EEG responses evoked by single pulse peripheral electrical stimulation. As this will be a multi-channel-readout, there would be a tremendous amount of peaks and latencies. Therefore, we only store the GMFP trace results in the metadata. 
"""
valid_keys = [
    "intensity_mA",
    "pulse_width_ms",
    "stimulation_target",
    "gmfp_neg_peaks_magnitude_uv",
    "gmfp_neg_peaks_latency_ms",
    "gmfp_pos_peaks_magnitude_uv",
    "gmfp_pos_peaks_latency_ms",
    "gmfp_zcr_latencies_ms",
]  #: valid keys for pes-erp
