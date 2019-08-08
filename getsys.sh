#!/bin/sh
_2016=/nfs_scratch/ekoenig4/MonoZprimeJet/ZprimeTools2016/CMSSW_10_2_10/src/ZprimeTools2016
_2017=/nfs_scratch/ekoenig4/MonoZprimeJet/ZprimeTools2017/CMSSW_10_2_10/src/ZprimeTools2017
_2018=/nfs_scratch/ekoenig4/MonoZprimeJet/ZprimeTools2018/CMSSW_10_2_10/src/ZprimeTools2018

echo $_2016
cp $_2016/Systematics_2016.root Systematics/
echo $_2017
cp $_2017/Systematics_2017.root Systematics/
echo $_2018
cp $_2018/Systematics_2018.root Systematics/
