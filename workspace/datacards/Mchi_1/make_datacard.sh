#!/bin/sh
combineCards.py sr_2017=../datacard_sr_2017 we_2017=../datacard_we_2017 wm_2017=../datacard_wm_2017 ze_2017=../datacard_ze_2017 zm_2017=../datacard_zm_2017 ga_2017=../datacard_ga_2017 > datacard
sed -i 's/Mchi1/Mchi1/g' datacard
sed -i 's/Mphi1000/Mphi$MASS/g' datacard
