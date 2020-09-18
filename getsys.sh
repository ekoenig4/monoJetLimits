#!/bin/sh
if [ ! -d Systematics ]; then mkdir Systematics; fi
#if [ ! -d Systematics/2016 ]; then mkdir Systematics/2016/; fi
if [ ! -d Systematics/2017 ]; then mkdir Systematics/2017/; fi
if [ ! -d Systematics/2018 ]; then mkdir Systematics/2018/; fi
_2016=/nfs_scratch/ekoenig4/MonoZprimeJet/CMSSW_10_2_10/src/monoJetTools/2016
_2017=/nfs_scratch/ekoenig4/MonoZprimeJet/CMSSW_10_2_10/src/monoJetTools/2017
_2018=/nfs_scratch/ekoenig4/MonoZprimeJet/CMSSW_10_2_10/src/monoJetTools/2018

#echo $_2016
#cp $_2016/Systematics/* Systematics/2016/
echo $_2017
cp $_2017/Systematics/* Systematics/2017/
echo $_2018
cp $_2018/Systematics/* Systematics/2018/
