#!/usr/bin/env python
import glob
import math
import re
import sys
import os
from plotting import plotGroups, crossSections

# tableRow = r"{dsName:<120} & {title:<25} & {muExp50:12} & {muObs:12} & {xs:15} \\"
tableRow = r"{title:<25} & {muExp50:12} & {muExpDeltaUp:12} & {muExpDeltaDown:12} & {muObs:12} & {xs:15} \\"

print tableRow.format(
        dsName="Dataset",
        title="Short title",
        muExp50=r"$\mu_{exp}$",
        muExpDeltaUp=r"$\delta^{+}\mu_{exp}$",
        muExpDeltaDown=r"$\delta^{-}\mu_{exp}$",
        muObs=r"$\mu_{obs}$",
        xs=r"$\sigma \cdot BR [pb]$"
    )
print r"\hline"

for fn in glob.glob(sys.argv[-1]+"/*/COMB_asympt.log"):
    nameRegex = re.compile(r"--signal ([^ ]*)")
    with open(os.path.dirname(fn)+"/runlimit.sh") as cfg:
        m = nameRegex.search(cfg.read(), re.MULTILINE)
        if not m:
            print "crap"
            continue
        name = m.groups()[0]
    pg, dsName = plotGroups.parseSpecialPlotGroup(name)
    title = pg._title
    fullDataset = dsName[0]
    xs = crossSections.crossSections[fullDataset]

    mus = {}
    muRegex = re.compile(r"Expected *([^%]*)%: r < (.*)$")
    muObsRegex = re.compile(r"Observed Limit: r < (.*)$")
    with open(fn) as fin:
        for line in fin:
            m = muRegex.match(line)
            if m:
                mus[m.groups()[0]] = m.groups()[1]
            m = muObsRegex.match(line)
            if m:
                mus['Obs'] = m.groups()[0]
    if len(mus) < 6:
        # print "Problem with", fn
        continue

    digits = str(int(math.ceil(-math.log(float(mus['84.0'])/float(mus['50.0'])-1, 10)))+1)
    def sigFig(val):
        return (r"%."+digits+"g") % float(val)

    print tableRow.format(
            dsName=fullDataset.replace('_', r'\_'),
            title=title,
            muExp50=sigFig(mus['50.0']),
            muExpDeltaUp=sigFig(mus['84.0']),
            muExpDeltaDown=sigFig(mus['16.0']),
            muObs=sigFig(mus['Obs']),
            xs="%.3g" % xs,
        )
