Annotation Fields
*****************

Every CacheFile has one or more original files. Each file comes with *original* annotations stored in its MetaData. Additionally, each TraceData within its own set of annotations. There is a set of fields common to all OriginAnnotations and TraceAnnotations, but they also have additional fields  which depend on the type of readin / readout used.

.. automodule:: offspect.cache.readout
   :noindex:
   :members: valid_trace_keys, can_vary_across_merged_files, must_be_identical_in_merged_file
   
.. automodule:: offspect.input.tms.cmep
   :noindex:
   :members: valid_keys
   
.. automodule:: offspect.input.tms.imep
   :noindex:
   :members: valid_keys
   
.. automodule:: offspect.input.tms.erp
   :noindex:
   :members: valid_keys
