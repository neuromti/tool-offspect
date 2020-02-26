Architecture
------------

This package consists of several modules and applications.

The first frontier will be a set of command-line tools which takes a set of
files (with exact number and type depending on the
`file-format <fileformats.html>`_) and prepares an event-file.

This will be implemented for various `file-formats <inputfiles.html>`_.

Following the `workflow <workflow.html>`_ prepares the event-file and populates
the traces-file.

Event-file
**********

The event-file is a yaml-formatted ascii-encoded file -> :code:`events_<identifier>.yml`

Saving and loading can be implement with `pyyaml <https://pyyaml.org/wiki/PyYAMLDocumentation>`_.

Traces-file
***********

The traces-file is a binary file containing a set of numpy.ndarrays in
binary format.


We still have to decide on the exact format, e.g. whether we store them as
dictionary in HDF5 -> :code:`traces_<identifier>.h5` or as a numpy file ->
:code:`traces_<identifier>.npz`.

Saving and loading can be implemented e.g. with `deepdish <https://deepdish.readthedocs.io/en/latest/io.html>`_
or :code:`numpy.savez` and :code:`numpy.load`.

Similar to the following two examples:

.. code-block:: python

    import deepdish as dd
    import numpy as np
    # initialize a trace for 64 channels and 1000 samples
    trace = np.zeros((64, 1000))
    # initialize the dictionary with the traces
    traces = {0: trace, 1 : trace}
    dd.io.save('traces_example.h5',  traces)
    loaded = dd.io.load("traces_example.h5")
    assert np.all(loaded[0] == traces[0])

or

.. code-block:: python

   import numpy as np
   fname = "traces_example.npz"
   trace = np.zeros((64, 1000))
   np.savez(fname, t0=trace, t1=trace)
   npzfile = np.load(fname)
   print(npzfile.files)
   # >>> ['t0', 't1']
   assert np.all(npzfile["t0"]==trace)

