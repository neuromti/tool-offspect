import numpy as np
from offspect.cache.attrs import decode
from offspect.cache.file import TraceAttributes, TraceData

# %%
def baseline(data, attrs):
    pre = decode(attrs["samples_pre_event"])
    shift = decode(attrs["onset_shift"]) or 0
    bl = data[: pre + shift].mean(0)
    data = data - bl
    return data


def detrend(data, attrs):
    slope = np.mean(np.diff(data), 0)
    correction = np.arange(0, len(data)) * slope
    data = data - correction
    return data


def linenoise(data, attrs):
    signal = data.copy()
    fs = decode(attrs["samplingrate"])
    timestep = 1 / fs
    original_len = len(signal)
    filter_order = 100
    while len(signal) < fs:
        signal = np.pad(signal, (1, 0), "constant", constant_values=(0))
    fourier = np.fft.fft(signal)
    freq = np.fft.fftfreq(len(signal), d=timestep)
    fidx = int(np.where(freq == 50)[0][0])
    fourier[fidx] = 0
    signal = np.real(np.fft.ifft(fourier))
    signal = signal[-original_len:]
    data[:] = signal
    return data


def flipsign(data, attrs):
    return -data


PreProcessor = {
    "baseline": baseline,
    "detrend": detrend,
    "linenoise": linenoise,
    "flipsign": flipsign,
}


def process_data(data, attrs, key: str = "_log", delim: str = " on ") -> TraceData:
    """return TraceData processed by the steps in the field indexed by key
                
        args
        ----
        data: TraceData
            the tracedata
        attrs:TraceAttributes
            the traceattributes
        key: str
            which field is used for logging the processing steps


        returns
        -------
        data: TraceData 
            the date stored for this trace, but processed with the steps performed 
        """
    if key in attrs.keys():
        log = decode(attrs[key])
        for event in log:
            step, when = event.split(delim)
            print("STEPS: Replaying", step, "from", when)
            data = PreProcessor[step](data, attrs)
    return data
