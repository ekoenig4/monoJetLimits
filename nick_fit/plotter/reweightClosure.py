#!/usr/bin/env python
import ROOT
import glob
import re

muRegex = re.compile(r"Expected *([^%]*)%: r < (.*)$")
def readExpLimit(fn):
    mus = {}
    with open(fn) as log:
        for line in log:
            m = muRegex.match(line)
            if m:
                mus[m.groups()[0]] = float(m.groups()[1])
    return mus

h = ROOT.TH1D("muClosure", "Closure;(#mu_{exp}^{reweight} - #mu_{exp}^{fullsim}) / #delta#mu_{exp}^{fullsim};Points", 20, -2, 2)
for fn in glob.glob("nloDM_reweighted/*/*/combine.log"):
    rwLimit = readExpLimit(fn)
    fsLimit = readExpLimit(fn.replace("_reweighted", "_fullsim"))
    if '50.0' not in rwLimit.keys():
        print "problem with", fn
        continue
    num = (rwLimit['50.0']-fsLimit['50.0'])
    denom = fsLimit['84.0']-fsLimit['50.0'] if num > 0 else fsLimit['50.0']-fsLimit['16.0']
    if abs(num/denom) > 2:
        print "big excursion in", fn, ":", num/denom
    h.Fill(num/denom)
h.Draw()
