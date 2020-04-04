from typing import Any
import yaml

__all__ = ["pass_value", "decode"]


def pass_value(value: Any) -> Any:
    return value


def decode(value: str) -> Any:
    return yaml.load(value, Loader=yaml.Loader)
