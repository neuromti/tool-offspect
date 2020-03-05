TMS recordings
--------------


.. toctree::
   :maxdepth: 1
   :caption: Protocols

   Smartmove robot </_autosummary/offspect.input.tms.smartmove>
   XDF protocol </_autosummary/offspect.input.tms.xdfprot>
   Matlab protocol </_autosummary/offspect.input.tms.matprot>


.. _support-link-coords:

Manually linking the coordinates
********************************

A big challenge is when coordinates have to be linked with each stimulus
manually. This can be done using e.g the labnotes, and would require manual
entry during visual inspection. We cansupport this reconstruction using
independently stored coordinate positions.

In our lab, this means the :code:`xml`-files stored by localite. When e.g. a
predefined grid was used, this file contains the xyz-coordinates of the target
positions. Usually, a grid with 6x6 nodes was used, and each target was
stimulated 5 times. This would have resulted in 180 stimuli and 36 target
coordinates. In these cases, we can attempt to prepopulate the
:class:`~.CacheFile` with this information.

An example how this could be implemented in Python can be found in the
`intens_tms repo <https://github.com/translationalneurosurgery/stroke-tms-maps/blob/master/intens_tms/clean/coords.py#L184>`_.
