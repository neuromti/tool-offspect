from typing import Any
import yaml
from pathlib import Path
import datetime


def decode(value: str) -> Any:
    "decode any value from string"
    return yaml.load(value, Loader=yaml.Loader)


def encode(value: Any) -> str:
    "encode any value to string for storing as TraceAttribute value"
    if type(value) == type(Path()):
        value = str(value)
    if type(value) == datetime.datetime:
        value = str(value)
    if type(value) == str:
        return value
    return yaml.dump(value, Dumper=yaml.Dumper).splitlines()[0]
