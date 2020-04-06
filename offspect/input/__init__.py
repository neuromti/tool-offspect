import importlib
from typing import Tuple, Callable


def get_protocol_handler(
    readin: str, readout: str, protocol: str
) -> Tuple[Callable, Callable]:
    print(f"Loading handler for {readin}-{readout} and {protocol} files")
    m = importlib.import_module(f"offspect.input.{readin}.{readout}.{protocol}")
    return m.prepare_annotations, m.cut_traces
