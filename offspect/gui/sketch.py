# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 10:41:15 2020

@author: Ethan
"""
from scipy import stats
import numpy as np
from offspect.api import CacheFile
cf = CacheFile(r"C:\Users\Ethan\Documents\GitHub\offline-inspect\merged.hdf5")
attrs = cf.get_trace_attrs(1)
traces = cf.get_trace_data(1)
from matplotlib import pyplot as plt

zcr = int(attrs['zcr_latency_ms'] + len(traces)/2)

data = traces
data = stats.zscore(data)
peakpos = [data.argmin(), data.argmax()]
val = [data.min(), data.max()]
vpp = val[1] - val[0]
timey = np.arange(0, len(data))

pulse_peak    = np.squeeze(np.where(np.diff(np.sign(np.diff(data[:,0])))<0))+1
pulse_trough  = np.squeeze(np.where(np.diff(np.sign(np.diff(data[:,0])))>0))+1

mep_peak   = 
mep_trough =



plt.plot(timey, data)
plt.plot(timey[peaks], data[peaks], 'ro')
plt.plot(timey[troughs], data[troughs], 'ro')
plt.vlines([timey[peakpos[0]]], val[0], np.mean(data), color="red", linestyle="dashed")
plt.vlines([timey[peakpos[1]]], val[1], np.mean(data), color="red", linestyle="dashed")




from offspect.cache.file import merge
files = ["fname1.hdf5","fname2.hdf5"]
merge("merged.hdf5", files)
