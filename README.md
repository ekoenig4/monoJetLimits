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
git clone https://github.com/ekoenig4/ZprimeLimits.git
```

# Instructions For Running Limits

Systematics files are generated using the PlotTool/saveplot.py(https://github.com/ekoenig4/ZprimeTools/blob/2016/PlotTool/saveplot.py) from ZrimeTools(https://github.com/ekoenig4/ZprimeTools)
A sample Systematics file can be found here https://www.hep.wisc.edu/~ekoenig4/Systematics/ChNemPtFrac_2016.sys.root

## Making the Workspace
The workspace is created with an input systematics root file.
```
./makeWorkspace.py -i path/to/name_of_sysfile.sys.root
```
At the top of the script there are lists of mx and mv files to exclude and include, it is currently setup to run the mx and mv values that can be compared.
The datacards created in makeWorkspace do not include the control regions by default this can be changed with the option
```
./makeWorkspace.py -i path/to/name_of_sysfile.sys.root --cr
```
The workspaces created are placed in the folder created called Limits/
The name of the workspace directory is created as name_of_sysfile.sys
Inside the workspace directory there are template datacards for each region contained in the systematics file, the workspace.root file that contains the information to run combine on, and a signal_scaling.json that contians the scaling for each signal sample to be applied to the limits at the end.
A directory is created for each value of Mx that was included in the makeWorkspace.py file.
Inside each Mx directory there is the datacard that is ran through combine. These datacards are setup to specify the mv value using the --mass option in combine. A file called mvlist is created in each Mx directory to specify the mv values to run using the mx value.

## Running Limits
Limits are run using the runlimits.py script.
```
./runlimits.py -d path/to/workspace/dir/
```
This script will go through each Mx directory and run all avaiable mv values that are specified in the mvlist file in the Mx directory, in parallel. To be able to run in serial and with the output use option
```
./runlimits.py -d path/to/workspace/dir/ --verbose
```
After the limits are run in all the Mx directories, the limits are collected in a json inside each Mx directory using combineTool.py
Once all the limit jsons are created, all the Mx directory jsons are combined into one json called limits.json in the workspace directory.
The limits.json has a map of mx values to mv vlaues that contain the signal scale factor and limits for that Mx_Mv combination.

## Plotting Limits
Limits are plotted using hte CLplotter.py script.
```
./CLplotter.py -d path/to/workspace/dir/
```
The script uses the limits.json file to plot the limits in both 1D and 2D plots. By default the script plots the 2D plot, the type of plot can be specified using
```
./CLplotter.py -d path/to/workspace/dir/ --version 1D (or 2D)
```
Inside the script the outdir_base can be changed to specify where the plots are saved to