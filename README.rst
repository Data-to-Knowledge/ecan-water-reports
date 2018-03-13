A Project Template for a Github project with code and webpage
=============================================================

This git repository contains sample skeleton of what is needed to set up a project
that can be compiled into a Python package in PyPI and to create a documentation
webpage. This repository is meant to be housed on a git platform like GitHub,
which can host both the code and the webpage.

There are three primary template sources: `sampleproject <https://github.com/pypa/sampleproject>`_, `python-packaging <https://python-packaging.readthedocs.io/en/latest/>`_, and `Automating GIS-processes <https://automating-gis-processes.github.io/2016>`_

The sampleproject and python-packaging describe how to prepare a Python project to package it for PyPI, while the Automating GIS-processes describes how to create very nice documentation (especially for natural scientists) using Sphinx and GitHub. `Readthedocs <https://readthedocs.org>`_ is used to run Sphinx and the associated code to create the website htmls, which then gets hosted on the Readthedocs servers. This is not necessary as the website can easily be hosted via GitHub as well. Readthedocs just automates the build process, which then doesn't need to performed by the user.

Only minor changes have been made from the original two repositories other than the removal or commenting out of certain parts due to the unnessecary bloatiness for a template (Automating GIS-processes) or functions that are unecessary for this kind of template (sampleproject). These can be esaily added back in if needed.

The associated documentation `site <https://packaging.python.org/tutorials/distributing-packages/>`_ for the sampleproject is the official PyPI packaging site and includes how to create wheels during the packaging process.

The documentation to create a conda package from a PyPI package can be found `here <https://conda.io/docs/user-guide/tutorials/build-pkgs-skeleton.html>`_.

The associated webpage for this repository can be found `here <http://project-template1.readthedocs.io>`_
