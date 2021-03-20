Succession
==========

A program to control running small jobs and there dependent.

This could be thought of as another challenger for Makes crown.

Why use Succession
------------------

Succession puts you in control of decision about what to run and
when to run it. Make, Scons, etc all have fairly difficult
to change policies on the 'up to date' decision. 

Succession allows you control of this through provides the templates
for the common options as standard.

Succession aims to be light weight, and lean on Python Standard
library wherever possible, by keeping successions core small 
and simple as possible the aim to make it easy to use and
understand.

Dependencies
------------
This project has do dependencies for running other then the  
python standard library. However a Pipfile contains dev dependencies
required for building the documentation


Documentation
-------------

Documentation is built using sphinx::

    cd docs;
    pipenv run ./build_from_repo.sh

