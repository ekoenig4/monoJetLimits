#!/bin/sh

runlimits() {
    ./runlimits.py -d $@
}
runimpacts() {
    ./runimpacts.py -d $@
}
runCRfit(){
    set -e
    ./runCRfit.py -d $@

    python PlotTool/plotCRfit.py -d $@ &
    ./runpulls.py -d $@ &
    wait
}

# runlimits $@ &
runimpacts $@ &
runCRfit $@ &
wait
echo Done
