from ROOT import *
import os
import sys

signals = ["ggh","vbf","wh","zh"]

output = sys.argv[1]
input = sys.argv[2]


print "Copying signal from %s to %s" % (input,output)

output = TFile(output,"update")
input = TFile(input)


for cat in output.GetListOfKeys():
    print cat.GetName()
    if output.GetDirectory(cat.GetName()):
        outd = output.GetDirectory(cat.GetName())
        ind = input.GetDirectory(cat.GetName())
        for signal in signals:
            print signal
            signal = ind.Get("signal_"+signal)
            outd.cd()
            signal.Write()
