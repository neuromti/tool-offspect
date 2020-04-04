"""
Contralateral MEPs induced by single pulse TMS
----------------------------------------------

This is a readout for a single channel EMG response evoked by single pulse transcranial magnetic stimulation. As this will be a single-channel-readout with a relatively clear waveform, we store only the magnitude of the first negative and positive peak and the zero-crossing latency.

"""
from offspect.cache.converter import Converter, exists, pass_value, encode, decode
from offspect.cache.readout import generic

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
]  #: valid keys for contralateral-mep

is_valid = Converter.factory(valid_keys, exists) + generic.is_valid
pass_value = Converter.factory(valid_keys, pass_value) + generic.pass_value
encode = Converter.factory(valid_keys, encode) + generic.encode
decode = Converter.factory(valid_keys, decode) + generic.decode
