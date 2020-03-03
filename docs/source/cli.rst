Command Line Interface
----------------------

   
offspect offers a command line interface. This interface can be accessed after installation of the package from the terminal, e.g. peek into a CacheFile with 

.. code-block:: bash

   offspect peek example.hdf5

offspect
~~~~~~~~
.. code-block:: none

   usage: offspect [-h] {peek,merge} ...
   
   Create, manipulate and inspect cachefiles for offline inspection of evoked
   potentials
   
   positional arguments:
     {peek,merge}
       peek        peek into a cachefile and print essential information
       merge       merge two cachefiles into one
   
   optional arguments:
     -h, --help    show this help message and exit


offspect peek
~~~~~~~~~~~~~
.. code-block:: none

   usage: offspect peek [-h] fname
   
   positional arguments:
     fname       filename to peek into
   
   optional arguments:
     -h, --help  show this help message and exit


offspect merge
~~~~~~~~~~~~~~
.. code-block:: none

   usage: offspect merge [-h] -t TO -f SOURCES [SOURCES ...] [-verbose]
   
   optional arguments:
     -h, --help            show this help message and exit
     -t TO, --to TO        filename to merge into. May not already exist
     -f SOURCES [SOURCES ...], --from SOURCES [SOURCES ...]
                           <Required> list of files to merge
     -verbose, -v          be more verbose


