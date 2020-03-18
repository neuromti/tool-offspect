from offspect.cache.readout import Converter, exists, pass_value, encode, decode

valid_origin_keys = [
    "channel_labels",
    "samples_post_event",
    "samples_pre_event",
    "samplingrate",
    "subject",
    "readout",
    "global_comment",
    "filedate",
    "history",
    "version",
]

valid_trace_keys = [
    "id"
    "event_name"
    "event_sample"
    "event_time"
    "xyz_coords"
    "onset_shift"
    "time_since_last_pulse_in_s"
    "reject"
    "comment"
    "examiner"
]

valid_keys = valid_origin_keys + valid_trace_keys

is_valid = Converter.factory(valid_keys, exists)
pass_value = Converter.factory(valid_keys, pass_value)
encode = Converter.factory(valid_keys, encode)
decode = Converter.factory(valid_keys, decode)
