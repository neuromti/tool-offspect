"""
Generic MetaData fields implemented in all readouts
---------------------------------------------------

More elaborate analysis requires custom-written scripts or readouts.
"""

must_be_identical_in_merged_file = [
    "channel_labels",
    "channel_of_interest",
    "samples_post_event",
    "samples_pre_event",
    "samplingrate",
    "subject",
    "readout",
    "readin",
    "version",
]
can_vary_across_merged_files = [
    "global_comment",
    "filedate",
]  #: information about the origin file

valid_origin_keys = must_be_identical_in_merged_file + can_vary_across_merged_files

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
