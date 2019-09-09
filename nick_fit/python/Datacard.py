#!/usr/bin/env python
from ROOT import *
import re
import math
from utilities import *
# Based on Nicks recipe from
# url here

class Datacard:
    def __init__(self,channel,doBin=False):
        self.doBin = doBin
        self.nSignals = 0
        self.channel = channel
        self.shapes = []
        self.observation = []
        self.rates = []  # To be a tuple (process name, rate), signals first!
        self.nuisances = {}  # To be a dict "nuisance name": {"process name": scale, ...}
        self.extras = set()
    def addShape(self,process,shapeFname):
        self.shapes.append(
            'shape %s * ../%s $CHANNEL/$PROCESS $CHANNEL/$PROCESS_$SYSTEMATIC' % (process,shapeFname)
            )
    def addObservable(self,ch_dir,useShape=True):
        data_obs = ch_dir.Get('data_obs')
        if self.doBin:
            for iBin in range(data_obs.GetNbinsX()):
                channel = "%s_%s" % (self.channel, binName(data_obs, iBin))
                self.observation.append('bin          %s' % channel)
                self.observation.append('observation  %.3f' % data_obs.GetBinContent(iBin+1))
        else:
            channel = self.channel
            self.observation.append('bin          %s' % channel)
            self.observation.append('observation  %.3f' % (data_obs.Integral() if useShape else -1))
    def addNominal(self,process,ch_dir,useShape=True,useStat=False):
        ch = self.channel
        nominalHist = ch_dir.Get(process)
        shapeName = "%s_%s" % (process, ch)
        if self.doBin:
            checkShape(nominalHist, shapeName)
            for iBin in range(nominalHist.GetNbinsX()):
                channel = "%s_%s" % (ch, binName(nominalHist, iBin))
                b = nominalHist.GetBinContent(iBin + 1)
                self.rates.append((process, b))
                if not useStat: return
                e = nominalHist.GetBinError(iBin + 1)
                if math.isnan(b) or math.isnan(e):
                    print "Warning: NAN found in %s_%s (%.3f-%.3f)" % (process, channel, nominalHist.GetXaxis().GetBinLowEdge(iBin + 1), nominalHist.GetXaxis().GetBinUpEdge(iBin + 1))
                    continue
                if b == 0.:
                    print "Warning: Zero bin in %s_%s (%.3f-%.3f)" % (process, channel, nominalHist.GetXaxis().GetBinLowEdge(iBin + 1), nominalHist.GetXaxis().GetBinUpEdge(iBin + 1))
                    # TODO: use effective lumi of sample to derive gmN bound!
                    # self.addNuisance("McStat_%s_%s gmN" % (channel, process), process, 0.1)
                else:
                    self.addNuisance("McStat_%s lnN" % (channel), process, 1.+e/b)
        else:
            channel = self.channel
            b = -1 if useShape else nominalHist.Integral()
            self.rates.append((process, b))
            if not useStat: return
            e = TMath.Sqrt( sum( nominalHist.GetBinError(i+1) * nominalHist.GetBinWidth(i+1)
                                 for i in range(nominalHist.GetNbinsX()) ) )
            if math.isnan(b) or math.isnan(e):
                print "Warning: NAN found in %s_%s" % (process, channel)
                return
            if b == 0.:
                print "Warning: Zero bin in %s_%s" % (process, channel)
                # TODO: use effective lumi of sample to derive gmN bound!
                # self.addNuisance("McStat_%s_%s gmN" % (channel, process), process, 0.1)
            else:
                self.addNuisance("McStat_%s lnN" % (channel), process, 1.+e/b)
    def addShapeNuisance(self,nuisName,process,ch_dir,invert=False):
        ch = self.channel
        histUp, histDown = ch_dir.Get('%s_%sUp' % (process,nuisName)),ch_dir.Get('%s_%sDown' % (process,nuisName))
        if invert:
            histUp, histDown = histDown, histUp
        nominalHist = ch_dir.Get(process) 
        def allBins(hist):
            return [hist.GetBinContent(i + 1) for i in range(hist.GetNbinsX())]
        if allBins(histUp) == allBins(histDown):
            print "Info: shape nuisance %s has no variation for process %s, skipping" % (nuisName, process)
            return
            
        hupratio = histUp.Clone("tmpratio1")
        hupratio.Divide(nominalHist)
        hdownratio = histDown.Clone("tmpratio2")
        hdownratio.Divide(nominalHist)
        
        if False: #args.doShapePlots:
            c = ROOT.TCanvas("%s_%s_%s" % (process, ch, nuisName))
            c.Divide(1,2)
            c.cd(1)
            nominalHist.SetLineColor(ROOT.kBlack)
            nominalHist.SetLineWidth(2)
            nominalHist.SetFillStyle(0)
            nominalHist.Draw("hist")
            histUp.SetLineColor(ROOT.kRed)
            histUp.SetLineWidth(2)
            histUp.SetFillStyle(0)
            histUp.Draw("histsame")
            histDown.SetLineColor(ROOT.kBlue)
            histDown.SetLineWidth(2)
            histDown.SetFillStyle(0)
            histDown.Draw("histsame")
            text = c.GetName() + " lnN %.3f / %.3f" % (histUp.Integral()/nominalHist.Integral(), histDown.Integral()/nominalHist.Integral())
            if invert:
                text += " INVERTED"
            l = ROOT.TLatex()
            ROOT.SetOwnership(l, False)
            l.SetNDC()
            l.SetTextSize(1.3*ROOT.gPad.GetTopMargin())
            l.SetTextFont(42)
            l.SetY(1-ROOT.gPad.GetTopMargin()-.1)
            l.SetTextAlign(33)
            l.SetX(1-ROOT.gPad.GetRightMargin()-.1)
            l.SetTitle(text)
            l.Draw()
            c.cd(2)
            hupratio.GetYaxis().SetTitle("Ratio")
            hupratio.Draw("hist")
            hupratio.GetYaxis().SetRangeUser(0.5, 1.5)
            hdownratio.Draw("histsame")
            if not os.path.exists("shapePlots"):
                os.makedirs("shapePlots")
            c.Print("shapePlots/%s.pdf" % c.GetName())

        shapeName = "%s_%s_%sUp" % (process, ch, nuisName)
        checkShape(histUp, shapeName)
        shapeName = "%s_%s_%sDown" % (process, ch, nuisName)
        checkShape(histDown, shapeName)
        if self.doBin:
            for iBin in range(histUp.GetNbinsX()):
                channel = "%s_%s" % (ch, binName(nominalHist, iBin))
                upR = hupratio.GetBinContent(iBin + 1)
                if upR <= 0.:
                    upR = 0.1
                downR = hdownratio.GetBinContent(iBin + 1)
                if downR <= 0.:
                    downR = 0.1
                self.addNuisance("%s lnN" % nuisName, process, (upR, downR))
        else:
            channel = self.channel
            self.addNuisance("%s shape" % nuisName, process, 1)
    def addNuisance(self,nuisName,process,rate):
        if nuisName not in self.nuisances:
            self.nuisances[nuisName] = {}
        self.nuisances[nuisName][process] = rate
