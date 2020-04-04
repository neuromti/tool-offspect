Architecture
------------

This package consists of several modules and applications.

The first frontier will be a set of command-line tools which takes a set of
files (with exact number and type depending on the file-format and
prepares an event-file.

This will be implemented for various `file-formats <inputfiles.html>`_.

Follow the `workflow <workflow.html>`_ to prepare the event-file and populates
the traces-file. This is mainly a `command-line-interface <cli.html>`_.

Additionally, there is a Python API to load CacheFiles, and which allow
manipulation of the metadata for each trace, and read-only access to global
metadata and the data for each trace.

.. toctree::
   :maxdepth: 2

   cachefile
   input
   readouts