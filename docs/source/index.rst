.. spycone documentation master file, created by
   sphinx-quickstart on Fri Apr  2 11:41:26 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Spycone - SPlicing-aware time-COurse Network Enricher
============================================================

Spycone is a python package that provides systematic analysis of time course transcriptomics data. It uses gene or isoform expression and a biological network as an input. It employs the sum of changes of all isoforms relative abundances (total isoform usage) across time points to detect IS events. Spycone further provides downstream analysis such as clustering by total isoform usage, gene set enrichment analysis, network enrichment, and splicing factors analysis. Below we describe the Spycone workflow in detail. . 



*************
Installation
*************

Prerequisite

Spycone is dependent on the pcst_fast library, which is not available through pip install. Please go to `the github page <https://github.com/fraenkel-lab/pcst_fast>`_ or run this command.::

   pip install https://github.com/fraenkel-lab/pcst_fast/archive/refs/tags/1.0.7.tar.gz


To install Spycone::

   pip install spycone

To install the latest development::

   git clone https://github.com/yollct/spycone.git
   cd spycone
   pip install .

==================
Contents
==================
.. toctree::
   :maxdepth: 2

   gene-level-workflow.ipynb
   alternative.ipynb
   api/index


* :ref:`search`
