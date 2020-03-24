#!/bin/sh
./runlimits.py -d $@ && \
    ./PlotTool/CLplotter.py -d $@ &
./runimpacts.py -d $@ &
./runCRfit.py -d $@ && \
    (python PlotTool/plotCRfit.py -d $@ & \
    ./runpulls.py -d $@) &

wait
