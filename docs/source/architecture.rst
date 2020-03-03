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

.. automodule:: offspect.cache.file
   :members: CacheFile, merge

.. automodule:: offspect.cache.check
   :members: check_consistency, check_valid_suffix, check_trace_attributes

Types
*****

.. automodule:: offspect.cache.check
   :noindex:
   :members: MetaData, MetaValue, Annotations, TraceAttributes, Trace, FileName


Valid Readouts
**************

.. automodule:: offspect.cache.check
   :noindex:
   :members: VALID_READOUTS, GENERIC_TRACEKEYS, SPECIFIC_TRACEKEYS