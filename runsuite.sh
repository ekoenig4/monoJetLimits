#!/bin/sh
./runlimits.py -d $@ || exit 1
./PlotTool/CLplotter.py -d $@ || exit 1
./runimpacts.py -d $@ || exit 1
./runpulls.py -d $@ || exit 1
./runCRfit.py -d $@ || exit 1
python PlotTool/plotCRfit.py -d $@ || exit 1
