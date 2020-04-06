import importlib
from typing import Tuple, Callable


def get_protocol_handler(
    readin: str, readout: str, protocol: str
) -> Tuple[Callable, Callable]:
    """get a handler for a specific readin and readout and recording protocol
    
    see also :func:`~offspect.cache.readout.get_valid_readouts`
    """
    print(f"Loading handler for {readin}-{readout} and {protocol} files")
    try:
        m = importlib.import_module(f"offspect.input.{readin}.{readout}.{protocol}")
        return m.prepare_annotations, m.cut_traces  # type: ignore
    except Exception:
        raise ImportError(
            f"offspect.input.{readin}.{readout}.{protocol} is invalid. Please define prepare_annotations and cut_traces"
        )
