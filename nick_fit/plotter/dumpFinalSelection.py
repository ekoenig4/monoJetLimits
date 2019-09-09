#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
import sys

bit = lambda i: 2**i

def chName(ch):
    if ch & bit(1):
        return 'EE'
    elif ch & bit(2):
        return 'EM'
    elif ch & bit(3):
        return 'MM'
    elif ch & (bit(4) | bit(5)):
        return '3L'
    elif ch & (bit(6) | bit(7)):
        return '4L'
    return 'XX'

blindBits = bit(1) | bit(3)

file0 = ROOT.TFile.Open(sys.argv[-1])
datasets = ['DoubleEG', 'DoubleMuon', 'SingleElectron', 'SingleMuon', 'MuonEG']
for dataset in datasets:
    t = file0.Get(dataset+"/finalSelection")
    for i in range(t.GetEntries()):
        t.GetEntry(i)
        tup = [dataset, t.run, t.lumi, t.event, chName(t.channel), t.pfMet, t.Zmass]
        if t.channel & blindBits:
            continue
        if t.pfMet > 100.:
            print ",".join(map(str, tup))
