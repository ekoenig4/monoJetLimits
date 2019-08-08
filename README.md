Follow below instructions to get HiggsCombine

[Official Documentation for HiggsCombined](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)
=================================================================================================================

CC7 release CMSSW_10_2_X HiggsCombined
===========================
```
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.0.1
scramv1 b clean; scramv1 b # always make a clean build
cd $CMSSW_BASE/src
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scram b -j
```
Mono-Z'-CombinedLimit
=====================
```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/
git clone https://github.com/ekoenig4/ZprimeLimits.git
```
