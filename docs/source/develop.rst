Development
-----------

Development can concern one of the four aspects of this package. Either the GUI,
the CLI, the loadable fileformats or the readouts allowed in the cachefile.

Developing Readouts
*******************

Currently implemented readouts can be found at :data:`~.VALID_READOUTS`.
Each readout comes with a definition of its :class:`~.TraceAttributes`, i.e.
a specific set of keys and types for their required values. HDF5 can only store
strings as keys and values, but during loading, every metadata will be parsed
with :py:func:`~.parse_attrs`, which uses :func:`ast.literal_eval` from the
Python standard library for safe parsing.

This means, the strings can be of any type which can be parsed with
:func:`ast.literal_eval`.

It is the responsibility of the developer to add the respective definitions as
one value to :data:`~.SPECIFIC_TRACEKEYS`, with the key being the string-name
of the new readout. Additionally, readout should be added to
:data:`~.VALID_READOUTS`.


Mock
****

Mock two xdf5 files using
:code:`python tests/mock/cache.py fname1.hdf5 fname2.hdf5` from the project
root.

