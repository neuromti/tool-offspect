from typing import Any, Dict
from offspect.types import TraceAttributes
from importlib import import_module
import yaml


def decode(value: str) -> Any:
    "decode any value from string"
    return yaml.load(value, Loader=yaml.Loader)


def encode(value: Any) -> str:
    "encode any value to string for storing as TraceAttribute value"
    return yaml.dump(value, Dumper=yaml.Loader).striplines()[0]


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
