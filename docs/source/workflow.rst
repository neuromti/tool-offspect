Workflow
--------

The workflow is described in the figure below. 


.. graphviz:: workflow.dot


There are several use cases for this software package. Every use case follows a similar workflow like the one described above. You select a specific set of source files, and initialize a new CacheFile from these files. 

Initialization is a two-step process. First, annotations are created. Second, these annotations are used to cut the recorded data for the desired channel into Traces. The CacheFile created in this fashion can then be visually inspected. 

Optional, you can fork a new CacheFile by copying its annotations and applying it on a new source file. This can be used to create a CacheFile with the same annotations, e.g. timestamps of triggers, rejection flags etc, but for a different EMG channel.  

You can also merge two CacheFiles together. This appends both source CacheFiles into a new CacheFile, and can be done recursively for multiple CacheFiles. The advantage lies in having only a single file for multiple source files, e.g. from multiple runs of the same measurement. 

For the use case of visual inspection of contralateral single-channel MEPs after TMS, there exist a CLI and an API.

CLI
***

Consider reading also the general CLI documentation :doc:`cli`.

.. automodule:: offspect.cli.tms
   :noindex:
   :members: cli_tms
   
   
API
***

The API is basd on the two functions `cut_traces` and `prepare_annotations` which have their specific implementation and function signature for each protocol. Look at the more in-depth documentation at :doc:`input`.