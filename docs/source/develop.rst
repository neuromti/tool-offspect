Development
-----------

Development can concern one of the four aspects of this package. Either the GUI, the CLI, the loadable fileformats or the readouts allowed in the cachefile.

.. _devreadout:

Developing Readouts
*******************

Currently implemented readouts can be found at :data:`~.VALID_READOUTS`. 
Each readout comes with a definition of its :class:`~.TraceAttributes`, i.e.
a specific set of keys and types for their required values. HDF5 can only store
strings as keys and values. When annotations are being accessed, it sensible to :py:func`~.decode` and :py:func`~.encode` for safe parsing. In general, we recommend that the value types are limited to :code:`str`, :code:`int`,:code:`float`, or :code:`List` of said types.

It is the responsibility of the developer to add the respective definitions for each readin / readout combination. To allow for a clear organization, you can find the protocol handlers in the `input` folder. There, each `readin` has its `readout` folder. In this lowest level, the handlers for the protocols are defined in their own modules, while the valid trace keys are defined in their `__init__.py`.


.. _developing the gui:

GUI test and development
************************

Mock two xdf5 files using :code:`python tests/mock/cache.py fname1.hdf5 fname2.hdf5` from the project root. Merge these two files with :code:`offspect merge -f fname1.hdf5 fname2.hdf5 -t merged.hdf5`. Peek into the merged file with :code:`offspect peek merged.hdf5`. This should give you the following output:

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