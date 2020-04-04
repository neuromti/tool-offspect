"""
ERPs induced by single pulse TMS
--------------------------------

This is a readout for EEG responses evoked by single pulse transcranial magnetic stimulation. As this will be a multi-channel-readout, there would be a tremendous amount of peaks and latencies. Therefore, we only store the GMFP trace results in the metadata.
"""
from offspect.cache.converter import Converter, exists, pass_value, encode, decode
from offspect.cache.readout import generic

command = "tms-erp"  #: command line parameter for this readout
valid_keys = [
    "stimulation_intensity_mso",
    "stimulation_intensity_didt",
    "xyz_coords",
    "gmfp_neg_peaks_magnitude_uv",
    "gmfp_neg_peaks_latency_ms",
    "gmfp_pos_peaks_magnitude_uv",
    "gmfp_pos_peaks_latency_ms",
    "gmfp_zcr_latencies_ms",
]  #: valid keys for tms-erp

is_valid = Converter.factory(valid_keys, exists) + generic.is_valid
pass_value = Converter.factory(valid_keys, pass_value) + generic.pass_value
encode = Converter.factory(valid_keys, encode) + generic.encode
decode = Converter.factory(valid_keys, decode) + generic.decode
