#!/bin/sh
./runlimits.py -d $@
./runimpacts.py -d $@
./runpulls.py -d $@
./runCRfit.py -d $@
