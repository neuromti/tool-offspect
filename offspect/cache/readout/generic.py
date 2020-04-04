"""
Generic MetaData fields implemented in all readouts
---------------------------------------------------

More elaborate analysis requires custom-written scripts or readouts.
"""
from offspect.cache.converter import Converter, exists, pass_value, encode, decode

valid_origin_keys = [
    "channel_labels",
    "channel_of_interest",
    "samples_post_event",
    "samples_pre_event",
    "samplingrate",
    "subject",
    "readout",
    "readin",
    "global_comment",
    "filedate",
    "history",
    "version",
]  #: information about the origin file

valid_trace_keys = [
    "id",
    "event_name",
    "event_sample",
    "event_time",
    "onset_shift",
    "time_since_last_pulse_in_s",
    "reject",
    "comment",
    "examiner",
]  #: information contained in every trace, regardless of readout

valid_keys = valid_origin_keys + valid_trace_keys

is_valid = Converter.factory(valid_keys, exists)
pass_value = Converter.factory(valid_keys, pass_value)
encode = Converter.factory(valid_keys, encode)
decode = Converter.factory(valid_keys, decode)
