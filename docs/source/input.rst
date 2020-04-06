Inputs
------

Different assessments, e.g. TMS Mappings, NMES ERP, or H-Wave assessments,
have different readouts (see :ref:`devreadout`), and therefore different information needs to be stored in the :class:`~.CacheFile` (see :doc:`annotations`).

Also, in the course of the last years, we used different protocols for the
same readouts. Each protocol might use different file-formats, different
number of files, or even within one file, different internal structures.

Therefore, we face different challenges for each implementation of each
protocol. In the following paragraphs these challenges are described.

.. toctree::
   :maxdepth: 1  
   :glob:

   input/*prot
   input/notes








