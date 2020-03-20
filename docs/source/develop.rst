Development
-----------

Development can concern one of the four aspects of this package. Either the GUI, the CLI, the loadable fileformats or the readouts allowed in the cachefile.

.. _devreadout:

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

.. _developing the gui:

GUI test and development
************************

Mock two xdf5 files using :code:`python tests/mock/cache.py fname1.hdf5 fname2.hdf5` from the project root. Merge these two files with :code:`offspect merge -f *.hdf5 -t merged.hdf5`. Peek into the merged file with :code:`offspect peek merged.hdf5`. This should give you the following output:

.. code-block:: none

   ------------------------------------------------------------------------------
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
   ------------------------------------------------------------------------------
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

Start visual inspection using the GUI with this file with :code:`offspect gui -f merged.hdf5` or run :code:`offspect gui` and select the desired cachefile using the menu. You can also set the gui resolution, see :doc:`cli` for more information.


Full Documentation
******************

.. toctree::
   :maxdepth: 1

   package