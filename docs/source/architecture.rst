Architecture
------------

This package consists of several modules and applications.

The first frontier will be a set of command-line tools which takes a set of
files (with exact number and type depending on the
`file-format <fileformats.html>`_) and prepares an event-file.

This will be implemented for various `file-formats <inputfiles.html>`_.

Following the `workflow <workflow.html>`_ prepares the event-file and populates
the traces-file.

Cache Manipulation
******************

.. automodule:: offspect.cache.hdf
   :members: CacheFile
