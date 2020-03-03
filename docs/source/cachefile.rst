CacheFile
---------

The python interface to the :py:class:`~.CacheFile` which checks for filename
validity during instantiation. When one of its properties are called, it loads
and parses the metadata and datasets fresh from the hdf5 and aggregatates them.


.. automodule:: offspect.cache.file
   :noindex:
   :members: CacheFile

Structural Conformity
*********************

For each readout, a specific set of fields must be in the metadata of a trace.
During parsing, the validity of the CacheFiles metadata will automatically
be checked with :func:`~.check_metadata`.
