#!/bin/sh
./runlimits.py -d $@ &
./runimpacts.py -d $@ &
./runCRfit.py -d $@ && \
    (python PlotTool/plotCRfit.py -d $@ & \
    ./runpulls.py -d $@) &

wait
echo Done
