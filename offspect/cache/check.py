from offspect.cache.readout import VALID_READOUTS


def isindex(x: str) -> bool:
    if x is None or x == "" or type(x) is not str:
        return False
    try:
        ix = int(x)
        if ix < 0:
            return False
    except ValueError:
        return False
    return (ix - float(x)) < 0.000001
