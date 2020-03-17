from typing import Dict, Any
from offspect.types import TraceAttributes


def decode(attrs: TraceAttributes) -> Dict[str, Any]:
    print("Hello world")
    return {"hello": "world"}


def encode(attrs: TraceAttributes) -> Dict[str, Any]:
    print("Hello world")
    return {"hello": "world"}
