[![status](https://github.com/translationalneurosurgery/offline-inspect/workflows/pytest/badge.svg)](https://github.com/translationalneurosurgery/offline-inspect/actions) [![Documentation Status](https://readthedocs.org/projects/offline-inspect/badge/?version=latest)](https://offline-inspect.readthedocs.io/en/latest/?badge=latest) [![Coverage Status](https://coveralls.io/repos/github/translationalneurosurgery/offline-inspect/badge.svg?branch=develop)](https://coveralls.io/github/translationalneurosurgery/offline-inspect?branch=develop) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://en.wikipedia.org/wiki/MIT_License)



This is a software package to convert and visually inspect event-related
potentials from a variety of  file formats

File format to implement
------------------------
- [ ] eego .cnt
- [ ] .xdf
- [ ] .mat

## Testing the GUI

##### Mock

Mock two xdf5 files using `python tests/mock/cache.py fname1.hdf5 fname2.hdf5` from the project root.

##### Merge

Merge these two files with `offspect merge -f *.hdf5 -t merged.hdf5`.

##### Peek
Peek into the merged file with `offspect peek merged.hdf5`. This should give you the following output:
```
-------------------------------------------------------------------------------
origin               : template_R001.xdf
filedate             : 1970-01-01 00:01:01
subject              : VnNn
samplingrate         : 1000
samples_pre_event    : 100
samples_post_event   : 100
channel_labels       : ['EDC_L']
readout              : contralateral_mep
global_comment       : patient was tired
history              :
version              : 0.0.1
traces_count         : 2
-------------------------------------------------------------------------------
origin               : template_R002.xdf
filedate             : 1970-01-01 23:59:59
subject              : VnNn
samplingrate         : 1000
samples_pre_event    : 100
samples_post_event   : 100
channel_labels       : ['EDC_L']
readout              : contralateral_mep
global_comment       :
history              :
version              : 0.0.1
traces_count         : 2

```

##### Inspect

start visual inspection of this file with `not implemented`