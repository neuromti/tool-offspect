Command Line Interface
----------------------

   
offspect offers a command line interface. This interface can be accessed after installation of the package from the terminal, e.g. peek into a CacheFile with 

.. code-block:: bash

   offspect peek example.hdf5

offspect
~~~~~~~~
.. code-block:: none

   usage: offspect [-h] {peek,merge,tms,pes,gui} ...
   
   Create, manipulate and inspect cachefiles for offline inspection of evoked
   potentials
   
   positional arguments:
     {peek,merge,tms,pes,gui}
       peek                peek into a cachefile and print essential information
       merge               merge two cachefiles into one
       tms                 prepare cachefiles for a tms protocol
       pes                 prepare cachefiles for a pes protocol
       gui                 start the visual inspection GUI
   
   optional arguments:
     -h, --help            show this help message and exit


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


offspect tms
~~~~~~~~~~~~
.. code-block:: none

   usage: offspect tms [-h] -t TO -f SOURCES [SOURCES ...] -r READOUT -c CHANNEL
                       -pp PREPOST [PREPOST ...]
                       [-e SELECT_EVENTS [SELECT_EVENTS ...]]
   
   optional arguments:
     -h, --help            show this help message and exit
     -t TO, --to TO        filename of the cachefile to be populated
     -f SOURCES [SOURCES ...], --from SOURCES [SOURCES ...]
                           <Required> list of input files
     -r READOUT, --readout READOUT
                           the desired readout, valid are: ['cmep', 'imep',
                           'erp']
     -c CHANNEL, --channel CHANNEL
                           the desired channel
     -pp PREPOST [PREPOST ...], --prepost PREPOST [PREPOST ...]
                           <Required> positional arguments of pre and post
                           duration
     -e SELECT_EVENTS [SELECT_EVENTS ...], --events SELECT_EVENTS [SELECT_EVENTS ...]
                           <Required> select event


offspect pes
~~~~~~~~~~~~
.. code-block:: none

   usage: offspect pes [-h] -t TO -f SOURCES [SOURCES ...] -r READOUT -c CHANNEL
                       -pp PREPOST [PREPOST ...]
                       [-e SELECT_EVENTS [SELECT_EVENTS ...]]
   
   optional arguments:
     -h, --help            show this help message and exit
     -t TO, --to TO        filename of the cachefile to be populated
     -f SOURCES [SOURCES ...], --from SOURCES [SOURCES ...]
                           <Required> list of input files
     -r READOUT, --readout READOUT
                           the desired readout, valid are: ['erp', 'mep']
     -c CHANNEL, --channel CHANNEL
                           the desired channel
     -pp PREPOST [PREPOST ...], --prepost PREPOST [PREPOST ...]
                           <Required> positional arguments of pre and post
                           duration
     -e SELECT_EVENTS [SELECT_EVENTS ...], --events SELECT_EVENTS [SELECT_EVENTS ...]
                           <Required> select event


offspect gui
~~~~~~~~~~~~
.. code-block:: none

   usage: offspect gui [-h] [-r RESOLUTION] [-f FILENAME]
   
   optional arguments:
     -h, --help            show this help message and exit
     -r RESOLUTION, --resolution RESOLUTION
                           Which resolution to use for the window. leave empty
                           for default, or set to LR or HR
     -f FILENAME, --file FILENAME
                           Which file to load during startup


