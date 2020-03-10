# Mono-Z' - CombinedLimit

Follow below instructions to get HiggsCombine

[Official Documentation for HiggsCombined](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)
=================================================================================================================

## CC7 release CMSSW_10_2_X HiggsCombined
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
## Mono-Z'-CombinedLimit
```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/
git clone -b mono-jet https://github.com/ekoenig4/ZprimeLimits.git
```

# Instructions For Running Limits

Systematics files are generated using the [PlotTool/saveplot.py](https://github.com/varuns23/monoJetTools/blob/master/PlotTool/saveplot.py) from [monoJetsTools](https://github.com/varuns23/monoJetTools)

## Making the Workspace
First a signal scaling json should be generated for one of the systematic files signals. This is used to scale the limits to similar value and scaled back to get the actual value.
```
python generate_scaling.py path/to/sysfile.sys.root
```
This will produce the json with scaling values for the signal contained in the sysfile
The workspace is created with an input systematics root file.
```
./makeWorkspace.py -i path/to/name_of_sysfile.sys.root
```
At the top of the script there are lists of mchi and mphi files to exclude and include, it is currently setup to run the mchi and mphi values that can be compared.
The workspaces created are placed in the folder created called Limits/
The name of the workspace directory is created as name_of_sysfile.sys
Inside the workspace directory there are template datacards for each region contained in the systematics file, the workspace.root file that contains the information to run combine on, and the signal_scaling.json that contians the scaling for each signal sample to be applied to the limits at the end.
A directory is created for each value of Mchi that was included in the makeWorkspace.py file.
Inside each Mchi directory there is the datacard that is ran through combine. These datacards are setup to specify the mphi value using the --mass option in combine. A file called mphilist is created in each Mchi directory to specify the mphi values to run using the mchi value.

## Running Limits
Limits are run using the runlimits.py script.
```
./runlimits.py -d path/to/workspace/dir.sys/
```
This script will go through each Mchi directory and run all avaiable mphi values that are specified in the mphilist file in the Mchi directory, in parallel. To be able to run in serial and with the output use option
```
./runlimits.py -d path/to/workspace/dir.sys/ --verbose
```
After the limits are run in all the Mchi directories, the limits are collected in a json inside each Mchi directory using combineTool.py
Once all the limit jsons are created, all the Mchi directory jsons are combined into one json called limits.json in the workspace directory.
The limits.json has a map of mchi values to mphi vlaues that contain the signal scale factor and limits for that Mchi_Mphi combination.

## Plotting Limits
Limits are plotted using hte CLplotter.py script.
```
./CLplotter.py -d path/to/workspace/dir.sys/
```
The script uses the limits.json file to plot the limits in both 1D and 2D plots. By default the script plots the 2D plot, the type of plot can be specified using
```
./CLplotter.py -d path/to/workspace/dir.sys/ --version 1D (or 2D)
```
Inside the script the outdir_base can be changed to specify where the plots are saved to
