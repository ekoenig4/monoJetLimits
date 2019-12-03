#!/bin/sh
./PlotTool/CLplotter.py -d $@
python PlotTool/plotCRfit.py -d $@
sh ratioplots.sh 
