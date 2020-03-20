.. offline-inspect documentation master file, created by
   sphinx-quickstart on Wed Feb 26 15:48:11 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to offline-inspect's documentation!
===========================================

.. _installation:

Installation
------------

Install the Python 3 package directly from github. To be able to do this, you have to `install git first <https://git-scm.com/>`_. Additionally, you need a Python 3 installation- We recommend `Anaconda <https://www.anaconda.com/distribution/>`_, especially if you are a beginner with Python. If you have an issue with installing it, chat us up on our slack channel. 

After these two general requisites have been installed, you can download and install the package from your terminal (e.g. git bash, linux bash or windows command prompt or anaconda prompt) as follows

.. code-block:: bash
   
   git clone https://github.com/translationalneurosurgery/tool-offspect.git
   cd tool-offspect
   pip install -r requirements.txt
   pip install -e .

If you have a fresh Anaconda Installation, this should work out of the box. Otherwise, try :code:`pip install wheel` first, as we might install some wheels with some precompiled libraries. Another solution to issues is setting up a fresh environment. You can do so with 

.. code-block:: bash

   pip install virtualenv
   virtualenv .env
   source .env/bin/activate # on linux or mac
   .env\Scripts\activate # on windows
   pip install -r requirements.txt
   pip install -e .
   # at a later stage, you can deactivate the environment with
   deactivate


Content
-------

.. toctree::
   :maxdepth: 2

   architecture
   workflow
   develop
   cli



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
