#!/bin/sh
combineCards.py sr_2016=../datacard_sr_2016 sr_2017=../datacard_sr_2017 sr_2018=../datacard_sr_2018 we_2016=../datacard_we_2016 we_2017=../datacard_we_2017 we_2018=../datacard_we_2018 wm_2016=../datacard_wm_2016 wm_2017=../datacard_wm_2017 wm_2018=../datacard_wm_2018 ze_2016=../datacard_ze_2016 ze_2017=../datacard_ze_2017 ze_2018=../datacard_ze_2018 zm_2016=../datacard_zm_2016 zm_2017=../datacard_zm_2017 zm_2018=../datacard_zm_2018 > datacard
sed -i 's/Mx1/Mx150/g' datacard
sed -i 's/Mv1000/Mv$MASS/g' datacard
