"""
Muscle Response induced by single pulse PES
-------------------------------------------

This is a readout for a muscle responses evoked by single pulse peripheral electrical stimulation.
"""
from offspect.cache.converter import Converter, exists, pass_value, encode, decode
from offspect.cache.readout import generic

valid_keys = [
    "intensity_mA",
    "pulse_width_ms",
    "stimulation_target",
    "neg_peak_magnitude_uv",
    "neg_peak_latency_ms",
    "pos_peak_magnitude_uv",
    "pos_peak_latency_ms",
    "zcr_latency_ms",
    "xyz_coords",
    "channel_of_interest",
]  #: valid keys for nmes-erp

is_valid = Converter.factory(valid_keys, exists) + generic.is_valid
pass_value = Converter.factory(valid_keys, pass_value) + generic.pass_value
encode = Converter.factory(valid_keys, encode) + generic.encode
decode = Converter.factory(valid_keys, decode) + generic.decode
