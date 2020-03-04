from ROOT import *
import sys
import os
import re
import json

scaleTo = 80.0

tfile = TFile.Open(sys.argv[1])
srdir = tfile.Get('sr')
pattern = re.compile('^Axial_Mchi\d+_Mphi\d+$')
signalmap = {key.GetName():srdir.Get(key.GetName()) for key in srdir.GetListOfKeys() if pattern.search(key.GetName()) }

for signal,hs in signalmap.iteritems():
    multi = scaleTo / hs.Integral()
    signalmap[signal] = multi

def WriteScaling(signal_scale,output='signal_scaling.json'):
    with open(output,"w") as f:
        json.dump(signal_scale,f)
WriteScaling(signalmap)
    
