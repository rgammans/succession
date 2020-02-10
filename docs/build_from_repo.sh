#!/bin/sh

#
# This file build the Succession documentation
# in a checked-out rpeo, with the repo version
# of succession, but without installing it.
#
#

PYTHONPATH=.. python3 ../succession/cli.py "$@"
