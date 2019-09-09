#!/usr/bin/env python

from ROOT import *
from Workspace import Workspace

processes = ['Mx10_Mv1000','ZJets','WJets','DiBoson','TTJets','DYJets','GJets','QCD']

def main():
    fname = "ChNemPtFrac_2016.sys.root"
    sysfile = TFile.Open(fname)
    ws = Workspace(sysfile)
    syslist = {
        'lumi': {
            'processes':processes,
            'rate':1.026
            },
        'et_trigg':{
            'processes':processes,
            'rate':1.01
            },
        'bjet_veto':{
            'processes':processes,
            'rate':1.02
            },
        'EWK_ZJets':{
            'processes':['ZJets'],
            'rate':[1.10]
            },
        'EWK_WJets':{
            'processes':['WJets'],
            'rate':[1.15]
            }
        }
    for channel,card in ws.cards.iteritems():
        card.addShape('*',fname)
        for sysName,info in syslist.iteritems():
            if card.nSignals == 0 and sysName == '${signal}': continue
            for i,process in enumerate(info['processes']):
                if type(info['rate']) == list: rate = info['rate'][i]
                else:                          rate = info['rate']
                card.addNuisance("%s lnN" % sysName,process,rate)
    ws.write()

if __name__ == "__main__": main()
