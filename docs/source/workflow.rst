Workflow
--------

The workflow is described in the figure below. There are several use cases for different protocols of data recording. Every protocol follows the same workflow. You select a specific set of source files, and initialize a new CacheFile from these files (see :ref:`init`). Afterwards, you can visually inspect the CacheFile (see :ref:`visinspect`). Obviously, the package needs to be installed first (see :ref:`installation`).


.. graphviz:: workflow.dot


.. _init:

Initialization
**************

Initialization is a two-step process. First, annotations are created. Second, these annotations are used to cut the recorded data for the desired channel into Traces. The CacheFile created in this fashion can then be visually inspected. All of this happens under the hood and this separation is only important to later allow easier forking. 

To create a CacheFile for one of our many doc:`input`, you have to open a terminal, e.g. Linux bash, Git bash on Windows or the windows command prompt. You have to specify the files from which you convert, the file into which you convert and various parameters to select channels, pre-post duration etc. Find `command line examples`_ below.  Note that a CacheFile always has the :code:`.hdf5`-suffix and is actually a file organized in the `Hierarchical Data Format <https://de.wikipedia.org/wiki/Hierarchical_Data_Format>`_. 


The basic command for converting TMS data to a CacheFile is :code:`offspect tms`, and you can get its signature and help with :code:`offspect tms -h`. Based on the files you hand it, the programm tries to automatically detect under which protocol they were recorded. This can fail - in that case post an `Issue <https://github.com/translationalneurosurgery/tool-offspect/issues>`_. If you have problems, chat with me on our slack. Consider reading also the general CLI documentation :doc:`cli`.

.. _command line examples:

.. automodule:: offspect.cli.tms
   :noindex:
   :members: cli_tms
   

Fork
++++

You can fork a new CacheFile by copying its annotations and applying it on a new source file. This can be used to create a CacheFile with the same annotations, e.g. timestamps of triggers, rejection flags etc, but for a different EMG channel.  


Merge
+++++
You can also merge two CacheFiles together. This appends both source CacheFiles into a new CacheFile, and can be done recursively for multiple CacheFiles. The advantage lies in having only a single file for multiple source files, e.g. from multiple runs of the same measurement. 

For the use case of visual inspection of contralateral single-channel MEPs after TMS, there exist a CLI and an API.

.. _visinspect:

Visual Inspection
*****************

After you were able to create a cachefile, you can visually inspect it. To do so, start the GUI. You start the GUI also from the command-line, simply by typing :code:`offspect gui`. You can switch between different resolutions and setups of the GUI using the :code:`-r` parameter. Currently, `LR`, `HR`, and `XS` are implemented. Additionally, you can tell the GUI to immediatly load a file, sidestepping the initial manual picking of a CacheFile with :code:`-f`.

Again, consider reading also the general CLI documentation :doc:`cli`. The GUI should be self-explanatory, but it certainly is in an early stage. If you have any issues or desire any new features or changes, post an `Issue <https://github.com/translationalneurosurgery/tool-offspect/issues>`_. If you have problems, chat with me or Ethan on our slack. 

If you do not have a CacheFile,.but still want to try it out, you can follow the instruction in the paragraph on :ref:`developing the gui` to mock a CacheFile. 

   
API
***

The API is basd on the two functions `cut_traces` and `prepare_annotations` which have their specific implementation and function signature for each protocol. Look at the more in-depth documentation at :doc:`input` and :doc:`package`. Please do in the current developement stage of this package not expect anything in the API to be stable.