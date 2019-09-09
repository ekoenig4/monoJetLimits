#!/usr/bin/env python
from ROOT import *
from os import getenv
from Workspace import Workspace

gSystem.Load("libHiggsAnalysisCombinedLimit.so")

def getRegion(dir,rfile,ws):
    dir.cd()

    data_obs = dir.Get('data_obs'); data_obs.SetDirectory(0)
    ws.addTemplate('data_obs_%s' % dir.GetName(),data_obs)
    
    ws.makeBinList('data_obs_SR',data_obs)

def createWorkspace():
    ws = Workspace('w','w')

    outfname = 'workspace.root'
    output = TFile(outfname,'recreate')
    var = RooRealVar('chnemptfrac','Ch + Nem P^{123}_{T} Fraction',0,1.1)
    ws.setVar(var)

    
    fbase = "ChNemPtFrac_2016.sys.root"
    cmssw_base = getenv("CMSSW_BASE")
    fname = "%s/src/HiggsAnalysis/CombinedLimit/ZprimeLimits/Systematics/2016/%s" % (cmssw_base,fbase)
    sysfile = TFile(fname)

    #-----Signal Region-----#
    dir_sr = sysfile.GetDirectory('sr')
    getRegion(dir_sr,sysfile,ws)

    output.cd()
    ws.Write()

if __name__ == "__main__":
    createWorkspace()
