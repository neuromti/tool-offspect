from typing import Any, Dict
from offspect.types import TraceAttributes
from importlib import import_module
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


def encode_attrs(attrs: Dict[str, Any]) -> TraceAttributes:
    readout = import_module(f"offspect.cache.readout.{attrs['readout']}")
    try:
        return readout.encode(attrs)  # type: ignore
    except AttributeError:
        raise NotImplementedError(f"{readout} is not implemented")


def decode_attrs(attrs: TraceAttributes) -> Dict[str, Any]:
    readout = import_module(f"offspect.cache.readout.{attrs['readout']}")
    try:
        return readout.decode(attrs)  # type: ignore
    except AttributeError:
        raise NotImplementedError(f"{readout} is not implemented")
