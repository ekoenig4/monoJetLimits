#!/usr/bin/env python
import argparse
import plotting
import ROOT
import os
import math
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True


def checkShape(shapeHist, name):
    negativeBins = False
    zeroBins = False
    for iBin in range(shapeHist.GetNbinsX()):
        b = shapeHist.GetBinContent(iBin + 1)
        if b < 0.:
            negativeBins = True
            shapeHist.SetBinContent(iBin + 1, 0.)
            shapeHist.SetBinError(iBin + 1, -b)
        elif b == 0.:
            zeroBins = True
    if negativeBins:
        # TODO: print if -vv or something
        print "Info: Negative bin content removed in shape histogram %s" % (name, )
    if zeroBins:
        # print "Info: Zero bin content found in shape histogram %s" % shapeHist.GetName()
        pass
    if shapeHist.Integral() == 0.:
        print "Warning: Integral zero in shape histogram %s" % (name, )
    if shapeHist.GetBinContent(0) != 0.:
        print "Info: zeroing underflow bin in shape histogram %s" % (name, )
        shapeHist.SetBinContent(0, 0.)
    if shapeHist.GetBinContent(shapeHist.GetNbinsX()+1) != 0.:
        print "Info: zeroing overflow bin in shape histogram %s" % (name, )
        shapeHist.SetBinContent(shapeHist.GetNbinsX()+1, 0.)


# Purpose: keep track of RooWorkspace and datacards together
class Workspace:
    def __init__(self):
        self.cards = {}
        self.nSignals = 0

    def addChannel(self, channel):
        self.cards[channel] = {
            "shapes": [],
            "observation": [],
            "rates": [],  # To be a tuple (process name, rate), signals first!
            "nuisances": {},  # To be a dict "nuisance name": {"process name": scale, ...}
            "extras": set(),
        }

    def write(self, makeGroups=False):
        for channel, card in self.cards.iteritems():
            with open("cards/card_%s" % channel, "w") as fout:
                # Headers
                fout.write("# Card for channel %s\n" % channel)
                fout.write("imax 1 # process in this card\n")
                fout.write("jmax %d # process in this card - 1\n" % (len(card["rates"])-1, ))
                fout.write("kmax %d # nuisances in this card\n" % len(card["nuisances"]))
                fout.write("-"*30 + "\n")
                for line in card["shapes"]:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                for line in card["observation"]:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                binLine = "{0:<40}".format("bin")
                procLine = "{0:<40}".format("process")
                indexLine = "{0:<40}".format("process")
                rateLine = "{0:<40}".format("rate")
                for i, tup in enumerate(card["rates"]):
                    binLine += "{0:>20}".format(channel)
                    procLine += "{0:>20}".format(tup[0])
                    indexLine += "{0:>20}".format(i - self.nSignals + 1)
                    rateLine += "{0:>20}".format("%.3f" % tup[1])
                for line in [binLine, procLine, indexLine, rateLine]:
                    fout.write(line+"\n")
                fout.write("-"*30 + "\n")
                for nuisance in sorted(card["nuisances"].keys()):
                    processScales = card["nuisances"][nuisance]
                    line = "{0:<40}".format(nuisance)
                    for process, _ in card["rates"]:
                        if process in processScales:
                            s = processScales[process]
                            if type(s) is tuple:
                                line += "{0:>20}".format("%.3f/%.3f" % s)
                            else:
                                line += "{0:>20}".format("%.3f" % s)
                        else:
                            line += "{0:>20}".format("-")
                    fout.write(line+"\n")
                if makeGroups:
                    def makeGroups(name, prefix):
                        group = [n.split(" ")[0] for n in card["nuisances"].keys() if prefix in n]
                        fout.write("%s group = %s\n" % (name, " ".join(group)))
                    makeGroups("theory", "Theo_")
                    makeGroups("mcStat", "Stat_")
                    makeGroups("CMS", "CMS_")
                for line in card["extras"]:
                    fout.write(line+"\n")


def main():
    parser = argparse.ArgumentParser(description="Makes plots and combine shapes from MonoZSelector output", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    def rootFileType(fileName):
        f = ROOT.TFile.Open(fileName)
        if not f:
            msg = "%s is not a valid ROOT file or could not be opened!" % fileName
            raise argparse.ArgumentTypeError(msg)
        return f

    parser.add_argument("inputFile", help="Input file(s) will be searched for datasets in order", type=rootFileType, nargs="+")

    dataOpts = parser.add_argument_group("Data options")
    dataOpts.add_argument("--asimov", help="Substitute data with Asimov mu=0 (i.e. pre-fit background expectation)", action="store_true")
    dataOpts.add_argument("--lumi", help="Luminosity (unit: 1/pb)", type=float, default=1000.)

    signalOpts = parser.add_argument_group("Signal options")
    signalOpts.add_argument("--signal", help="Signal process plotGroup(s)", action="append")

    bkgOpts = parser.add_argument_group("Background options")
    bkgOpts.add_argument("--stack", help="Stack these plotGroups for backgrounds (bottom-up)", default="Nonresonant,ZZ2l2nu,WZ3lnu,Other,DrellYan")

    callbackOpts = parser.add_argument_group("Histogram modification options")
    callbackOpts.add_argument("--projX", help="Call TH2D::ProjectionX, with min and max Y bin", nargs=2, default=None)
    callbackOpts.add_argument("--rebin", help="Specify alternate binning in comma-separated list", default=None)

    shapeOpts = parser.add_argument_group("Shape building options")
    shapeOpts.add_argument("--channel", "-c", help="Make shapes for channel", action="append", required=True)
    shapeOpts.add_argument("--variable", help="Variable for which to extract shapes from", default="pfMet")
    shapeOpts.add_argument("--makeGroups", help="Add nuisance groups", action="store_true")
    shapeOpts.add_argument("--doShapePlots", help="Plot all shapes that went into the card in shapePlots directory", action="store_true")
    shapeOpts.add_argument("--perBinNorm", help="Per-bin Diboson normalizations", action="store_true")
    shapeOpts.add_argument("--noVVDYcr", help="Drop VV and Drell-Yan control regions", action="store_true")
    shapeOpts.add_argument("--noNRBinflate", help="Don't add 20% addl. uncertainty to nonresonant CR to SR transfer factor", action="store_true")

    args = parser.parse_args()

    # -----
    args.callback = plotting.buildCallback(args)

    selectorResults = []
    for inFile in args.inputFile:
        res = plotting.SelectorResult(inFile, luminosity=args.lumi)
        selectorResults.append(res)
    anaResult = plotting.AnalysisResult(args, selectorResults)

    # Suppress Info messages from TCanvas::Print() calls
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    ws = Workspace()

    ws.nSignals = len(args.signal) if args.signal else 0

    def binName(hist, iBin):
        return "bin%dto%d" % (hist.GetXaxis().GetBinLowEdge(iBin + 1), hist.GetXaxis().GetBinUpEdge(iBin + 1))

    for ch in args.channel:
        def addNuisance(card, nuisName, process, rate):
            if nuisName not in card["nuisances"]:
                card["nuisances"][nuisName] = {}
            card["nuisances"][nuisName][process] = rate

        shapeHistName = "%s_%s" % (ch, args.variable)

        # Add observation
        data_obs, = anaResult.plotGroup("Data").getShape(shapeHistName, None, args.callback)
        for iBin in range(data_obs.GetNbinsX()):
            channel = "%s_%s" % (ch, binName(data_obs, iBin))
            ws.addChannel(channel)
            card = ws.cards[channel]
            card["observation"].append("bin          %s" % channel)
            card["observation"].append("observation  %.3f" % data_obs.GetBinContent(iBin+1))

        def addNominal(process):
            nominalHist, = anaResult.plotGroup(process).getShape(shapeHistName, None, args.callback)
            shapeName = "%s_%s" % (process, ch)
            checkShape(nominalHist, shapeName)
            for iBin in range(nominalHist.GetNbinsX()):
                channel = "%s_%s" % (ch, binName(nominalHist, iBin))
                card = ws.cards[channel]
                b = nominalHist.GetBinContent(iBin + 1)
                card["rates"].append((process, b))
                e = nominalHist.GetBinError(iBin + 1)
                if math.isnan(b) or math.isnan(e):
                    print "Warning: NAN found in %s_%s (%.0f-%.0f)" % (process, channel, nominalHist.GetXaxis().GetBinLowEdge(iBin + 1), nominalHist.GetXaxis().GetBinUpEdge(iBin + 1))
                    continue
                if b == 0.:
                    print "Warning: Zero bin in %s_%s (%.0f-%.0f)" % (process, channel, nominalHist.GetXaxis().GetBinLowEdge(iBin + 1), nominalHist.GetXaxis().GetBinUpEdge(iBin + 1))
                    # TODO: use effective lumi of sample to derive gmN bound!
                    # addNuisance(card, "McStat_%s_%s gmN" % (channel, process), process, 0.1)
                else:
                    addNuisance(card, "McStat_%s_%s lnN" % (channel, process), process, 1.+e/b)

        def addShapeNuisance(process, nuisance, cardName, invert=False):
            histUp, histDown = anaResult.plotGroup(process).getShape(shapeHistName, nuisance, args.callback)
            if invert:
                histUp, histDown = histDown, histUp
            nominalHist, = anaResult.plotGroup(process).getShape(shapeHistName, None, args.callback)
            def allBins(hist):
                return [hist.GetBinContent(i + 1) for i in range(hist.GetNbinsX())]
            if allBins(histUp) == allBins(histDown):
                print "Info: shape nuisance %s has no variation for process %s, skipping" % (nuisance, process)
                return

            hupratio = histUp.Clone("tmpratio1")
            hupratio.Divide(nominalHist)
            hdownratio = histDown.Clone("tmpratio2")
            hdownratio.Divide(nominalHist)

            if args.doShapePlots:
                c = ROOT.TCanvas("%s_%s_%s" % (process, ch, cardName))
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

            shapeName = "%s_%s_%sUp" % (process, ch, cardName)
            checkShape(histUp, shapeName)
            shapeName = "%s_%s_%sDown" % (process, ch, cardName)
            checkShape(histDown, shapeName)
            for iBin in range(histUp.GetNbinsX()):
                channel = "%s_%s" % (ch, binName(nominalHist, iBin))
                card = ws.cards[channel]
                upR = hupratio.GetBinContent(iBin + 1)
                if upR <= 0.:
                  upR = 0.1
                downR = hdownratio.GetBinContent(iBin + 1)
                if downR <= 0.:
                  downR = 0.1
                addNuisance(card, "%s lnN" % cardName, process, (upR, downR))

        # Correlated systematics common to all MC
        for pg in anaResult.signalGroups + anaResult.stackGroups:
            process = pg._name
            addNominal(process)
            addShapeNuisance(process, "ElectronEn", "CMS_Scale_el")
            addShapeNuisance(process, "ElectronSF", "CMS_Eff_el")
            addShapeNuisance(process, "MuonEn", "CMS_Scale_mu")
            addShapeNuisance(process, "MuonSF", "CMS_Eff_mu")
            addShapeNuisance(process, "JetEn", "CMS_JES")
            addShapeNuisance(process, "JetRes", "CMS_JER")
            addShapeNuisance(process, "UnclusteredEn", "CMS_UES")
            addShapeNuisance(process, "Btag", "CMS_Scale_bJet")
            addShapeNuisance(process, "Pileup", "CMS_Scale_pileup")
            for iBin in range(data_obs.GetNbinsX()):
                bn = binName(data_obs, iBin)
                channel = "%s_%s" % (ch, bn)
                card = ws.cards[channel]
                addNuisance(card, "CMS_lumi_2016 lnN", process, 1.026)

        # Uncorrelated theory uncertainties in signal and main backgrounds
        theoBkgs = []
        if ch in ['ee', 'mm', 'll', 'lll']:
            theoBkgs.append(anaResult.plotGroup("WZ3lnu"))
        if ch in ['ee', 'mm', 'll']:
            theoBkgs.append(anaResult.plotGroup("qqZZ2l2nu"))
        if ch in ['llll']:
            theoBkgs.append(anaResult.plotGroup("qqZZ4l"))
        if ch in ['lll']:
            theoBkgs.append(anaResult.plotGroup("ZGamma"))
        for pg in theoBkgs + anaResult.signalGroups:
            process = pg._name
            if 'nloDM' in process or 'nloSMM' in process:
                # LHE weights are completely broken in most of the DM samples
                # Put in some dummy systematics, like it matters...
                for iBin in range(data_obs.GetNbinsX()):
                    bn = binName(data_obs, iBin)
                    channel = "%s_%s" % (ch, bn)
                    card = ws.cards[channel]
                    addNuisance(card, "Theo_pdfAlphaS_%s lnN" % process, process, 1.01)
                    addNuisance(card, "Theo_factRenormScale_%s lnN" % process, process, 1.05)
                continue
            if process in ['WZ3lnu', 'qqZZ2l2nu', 'qqZZ4l']:
                addShapeNuisance(process, "factRenormScale", "Theo_factRenormScale_VV")
            else:
                addShapeNuisance(process, "factRenormScale", "Theo_factRenormScale_%s" % process)
            if process in ['WZ3lnu']:
                # Anti-correlate with ZZ
                addShapeNuisance(process, "KFactors", "Theo_VVewkFactors", invert=True)
            if process in ['qqZZ2l2nu', 'qqZZ4l']:
                addShapeNuisance(process, "pdf", "Theo_pdfAlphaS_ZZ")
                addShapeNuisance(process, "KFactors", "Theo_VVewkFactors")
            elif '0jDM' in process or 'ToDM' in process:
                addShapeNuisance(process, "pdfHess", "Theo_pdfAlphaS_%s" % process)
            else:
                addShapeNuisance(process, "pdf", "Theo_pdfAlphaS_%s" % process)

        for iBin in range(data_obs.GetNbinsX()):
            bn = binName(data_obs, iBin)
            channel = "%s_%s" % (ch, bn)
            card = ws.cards[channel]

            if ch == 'ee':
                card["extras"].add("NRBnorm_ReSquared rateParam ee* Nonresonant 1 [0.01,10]")
                if not args.noNRBinflate:
                    addNuisance(card, "NRBnorm_Inflate lnN", "Nonresonant", 1.2)
            elif ch == 'mm':
                card["extras"].add("NRBnorm_RmSquared rateParam mm* Nonresonant 1 [0.01,10]")
                if not args.noNRBinflate:
                    addNuisance(card, "NRBnorm_Inflate lnN", "Nonresonant", 1.2)
            elif ch == 'll':
                card["extras"].add("NRBnorm_RmSquared rateParam ll* Nonresonant 1 [0.01,10]")
                card["extras"].add("NRBnorm_ReSquared rateParam ll* Nonresonant @0 NRBnorm_RmSquared")
                addNuisance(card, "NRBnorm_Inflate lnN", "Nonresonant", 1.2)
            elif ch == 'em':
                card["extras"].add("NRBnorm_ReRm rateParam em* Nonresonant sqrt(@0*@1) NRBnorm_ReSquared,NRBnorm_RmSquared")

            vvNormName = bn if args.perBinNorm else 'allBins'

            if ch in ['ee', 'mm', 'll'] and not args.noVVDYcr:
                if bn != 'bin50to100':
                    card["extras"].add("ZZWZNorm_%s rateParam %s_%s qqZZ2l2nu 1. [0.01,10]" % (vvNormName, ch, bn))
                    card["extras"].add("ZZWZNorm_%s rateParam %s_%s ggZZ2l2nu 1. [0.01,10]" % (vvNormName, ch, bn))
                    card["extras"].add("ZZWZNorm_%s rateParam %s_%s WZ3lnu 1. [0.01,10]" % (vvNormName, ch, bn))
                    addNuisance(card, "CMS_InflateDY2lNorm lnN", "DrellYan", 2.)
                card["extras"].add("DrellYanNorm rateParam %s_%s DrellYan 1. [0.01,10]" % (ch, bn))
            elif ch in ['ee', 'mm', 'll']:
                addNuisance(card, "CMS_NonPromptLepWZinSR lnN", "WZ3lnu", 1.03)
            elif ch == 'lll':
                card["extras"].add("ZZWZNorm_%s rateParam %s_%s WZ3lnu 1. [0.01,10]" % (vvNormName, ch, bn))
                addNuisance(card, "CMS_NonPromptLepDYinWZ lnN", "NonPromptDY", 1.3)
            elif ch == 'llll':
                card["extras"].add("ZZWZNorm_%s rateParam %s_%s qqZZ4l 1. [0.01,10]" % (vvNormName, ch, bn))
                card["extras"].add("ZZWZNorm_%s rateParam %s_%s ggZZ4l 1. [0.01,10]" % (vvNormName, ch, bn))
                addNuisance(card, "CMS_InflateOther4lNorm lnN", "Other4l", 1.4)

    ws.write(makeGroups=args.makeGroups)


if __name__ == "__main__":
    main()
