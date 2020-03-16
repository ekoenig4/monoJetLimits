#!/bin/sh
# ./runlimits.py -d $@ || exit 1
# ./PlotTool/CLplotter.py -d $@ || exit 1
./runimpacts.py -d $@ &
./runCRfit.py -d $@ && \
    (python PlotTool/plotCRfit.py -d $@ & \
    ./runpulls.py -d $@) &
