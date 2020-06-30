Command Line Interface
----------------------

   
offspect offers a command line interface. This interface can be accessed after installation of the package from the terminal, e.g. peek into a CacheFile with 

.. code-block:: bash

   offspect peek example.hdf5

offspect
~~~~~~~~
.. code-block:: none

   usage: offspect [-h] {peek,merge,tms,gui,plot} ...
   
   Create, manipulate and inspect cachefiles for offline inspection of evoked
   potentials
   
   positional arguments:
     {peek,merge,tms,gui,plot}
       peek                peek into a cachefile and print essential information
       merge               merge two cachefiles into one
       tms                 prepare cachefiles for a tms protocol
       gui                 start the visual inspection GUI
       plot                plot the map for a cachefile
   
   optional arguments:
     -h, --help            show this help message and exit


offspect peek
~~~~~~~~~~~~~
.. code-block:: none

   usage: offspect peek [-h] [-s SIMILARITY] fname
   
   positional arguments:
     fname                 filename to peek into
   
   optional arguments:
     -h, --help            show this help message and exit
     -s SIMILARITY, --similarity-threshold SIMILARITY
                           the threshold for Pearson's r. If this threshold is
                           passed, peek warns that the traces are similar.
                           Example: -s 0.75


offspect merge
~~~~~~~~~~~~~~
.. code-block:: none

   usage: offspect merge [-h] -t TO -f SOURCES [SOURCES ...] [--verbose]
   
   optional arguments:
     -h, --help            show this help message and exit
     -t TO, --to TO        filename to merge into. May not already exist
     -f SOURCES [SOURCES ...], --from SOURCES [SOURCES ...]
                           <Required> list of files to merge
     --verbose, -v         be more verbose


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
                           the desired readout, valid are: ['imep', 'cmep',
                           'erp']
     -c CHANNEL, --channel CHANNEL
                           the desired channel
     -pp PREPOST [PREPOST ...], --prepost PREPOST [PREPOST ...]
                           <Required> positional arguments of pre and post
                           duration
     -e SELECT_EVENTS [SELECT_EVENTS ...], --events SELECT_EVENTS [SELECT_EVENTS ...]
                           <Required> select events, e.g. stream and name or
                           names depending on protocol


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


offspect plot
~~~~~~~~~~~~~
.. code-block:: none

   usage: offspect plot [-h] -f CFNAME [-t SFNAME] [--kwargs KWARGS]
   
   optional arguments:
     -h, --help            show this help message and exit
     -f CFNAME, --filename CFNAME
                           Which cachefile to plot
     -t SFNAME, --figname SFNAME
                           The name of the imagefile to save the plot
     --kwargs KWARGS       A dictionary of additional keyword arguments to
                           finetune the plotting


