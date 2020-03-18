from typing import Any, List
import yaml

__all__ = ["encode"]


def encode(value: Any) -> str:
    return yaml.dump(value, Dumper=yaml.Dumper).splitlines()[0]
