from offspect.types import TraceAttributes
from typing import Dict, Any
from offspect.cache._check.converter import Converter, key_exists, pass_value


check_required_keys_exist = Converter(
    channel_labels=key_exists,
    samples_post_event=key_exists,
    samples_pre_event=key_exists,
    samplingrate=key_exists,
    subject=key_exists,
    readout=key_exists,
    global_comment=key_exists,
    filedate=key_exists,
    history=key_exists,
    version=key_exists,
)

filter_required_keys = Converter(
    channel_labels=pass_value,
    samples_post_event=pass_value,
    samples_pre_event=pass_value,
    samplingrate=pass_value,
    subject=pass_value,
    readout=pass_value,
    global_comment=pass_value,
    filedate=pass_value,
    history=pass_value,
    version=pass_value,
)

decode_required_keys = Converter(
    channel_labels=pass_value,
    samples_post_event=pass_value,
    samples_pre_event=pass_value,
    samplingrate=pass_value,
    subject=pass_value,
    readout=pass_value,
    global_comment=pass_value,
    filedate=pass_value,
    history=pass_value,
    version=pass_value,
)


def decode(attrs: Dict[str, Any]) -> Dict[str, Any]:
    if all(check_required_keys_exist(**attrs).values()):
        return {"hello": "world"}
    else:
        raise Exception()
