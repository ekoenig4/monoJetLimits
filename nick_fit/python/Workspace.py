#!/usr/bin/env python
from ROOT import *
import re
import math
import os
from Datacard import Datacard
from utilities import *
# Based on Nicks recipe from
# url here


mclist = ['ZJets','WJets','DiBoson','TTJets','DYJets','GJets','QCD']

class Workspace:
    def __init__(self,sysfile=None,signal_regex=re.compile(r'Mx\d+_Mv\d+$'),doBin=False):
        self.doBin = doBin
        self.cards = {}
        if type(sysfile) == str: sysfile = TFile.Open(sysfile)
        self.sysfile = sysfile
        self.ch_dirs = []
        self.signal_regex = signal_regex
        if sysfile != None: self.parseSysfile()
    def parseSysfile(self,sysfile=None):
        if sysfile == None: sysfile = self.sysfile
        for key in sysfile.GetListOfKeys():
            ch_dir = sysfile.GetDirectory(key.GetName())
            if ch_dir == None: continue
            self.ch_dirs.append(ch_dir)
            self.addChannel(ch_dir.GetName())
            self.fillChannel(ch_dir)
    def fillChannel(self, ch_dir):
        if type(ch_dir) != TDirectoryFile: return
        ch = ch_dir.GetName()
        if ch not in self.cards: self.addChannel(ch)
        hasSignal = any( self.signal_regex.match(key.GetName()) for key in ch_dir.GetListOfKeys() )
        ch = ch_dir.GetName()
        card = self.cards[ch]

        card.addObservable(ch_dir)
        
        signal = []
        if hasSignal:
            signal = [ key.GetName() for key in ch_dir.GetListOfKeys()
                       if self.signal_regex.match(key.GetName()) ]
            signal = ["Mx10_Mv1000"]
            card.nSignals = len(signal)
        
        for process in signal + mclist:
            card.addNominal(process,ch_dir)
            shapeNuisances = [ nuis.GetName().split('_')[-1].replace('Up','')
                              for nuis in ch_dir.GetListOfKeys()
                              if process in nuis.GetName() and 'Up' in nuis.GetName() ]
            for shapeNuisance in shapeNuisances:
                card.addShapeNuisance(shapeNuisance,process,ch_dir)
    
    def addChannel(self, channel):
        self.cards[channel] = Datacard(channel,doBin=self.doBin)

    def write(self, makeGroups=False):
        if not os.path.isdir('cards'): os.mkdir('cards')
        for channel, card in self.cards.iteritems():
            with open("cards/card_%s" % channel, "w") as fout:
                # Headers
                fout.write("# Card for channel %s\n" % channel)
                fout.write("imax 1 # process in this card\n")
                fout.write("jmax %d # process in this card - 1\n" % (len(card.rates)-1, ))
                fout.write("kmax %d # nuisances in this card\n" % len(card.nuisances))
                fout.write("-"*30 + "\n")
                for line in card.shapes:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                for line in card.observation:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                binLine = "{0:<20}".format("bin")
                procLine = "{0:<20}".format("process")
                indexLine = "{0:<20}".format("process")
                rateLine = "{0:<20}".format("rate")
                for i, tup in enumerate(card.rates):
                    binLine += "{0:<20}".format(channel)
                    procLine += "{0:<20}".format(tup[0])
                    indexLine += "{0:<20}".format(i - card.nSignals + 1)
                    rateLine += "{0:<20}".format("%.3f" % tup[1])
                for line in [binLine, procLine, indexLine, rateLine]:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                for nuisance in sorted(card.nuisances.keys()):
                    processScales = card.nuisances[nuisance]
                    line = "{0:<20}".format(nuisance)
                    for process, _ in card.rates:
                        if process in processScales:
                            s = processScales[process]
                            if type(s) is tuple:
                                line += "{0:<20}".format("%.3f/%.3f" % s)
                            else:
                                line += "{0:<20}".format("%.3f" % s)
                        else:
                            line += "{0:<20}".format("-")
                    fout.write(line+"\n")
                if makeGroups:
                    def makeGroups(name, prefix):
                        group = [n.split(" ")[0] for n in card.nuisances.keys() if prefix in n]
                        fout.write("%s group = %s\n" % (name, " ".join(group)))
                    makeGroups("theory", "Theo_")
                    makeGroups("mcStat", "Stat_")
                    makeGroups("CMS", "CMS_")
                for line in card.extras:
                    fout.write(line+"\n")
