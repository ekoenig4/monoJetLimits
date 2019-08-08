Follow below instructions to get HiggsCombine

<a href="http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/">Official Documentation for HiggsCombined<\a>
=================================================================================================================

CC7 release CMSSW_10_2_X HiggsCombined
===========================
```
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.0.1
scramv1 b clean; scramv1 b -j 24# always make a clean build
```
Instructions for getting Mono-Z' Combine Code
Mono-Z'-CombinedLimit
=====================
```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/
git clone https://github.com/ekoenig4/ZprimeLimits.git
```
