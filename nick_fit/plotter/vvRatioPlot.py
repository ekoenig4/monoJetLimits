#!/usr/bin/env python
import ROOT
import plotting
import plotting.styles as styles
from plotting.plotGroups import allPlotGroups
import array
import math
# ROOT.gROOT.SetBatch(True)
# ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptDate(False)
plotting.styles.forceStyle()

f = ROOT.TFile("resample_data.root")
tree = f.Get("resample_fit_b")
data = f.Get("data_obs")
binning = [100,120,150,180,200,250,300,350,400,500,600]
lllStack="WZ3lnu,ZGamma,Other3l,NonPromptDY".split(',')
llllStack="qqZZ4l,ggZZ4l,Other4l".split(',')
channel = "ratio"

plotName = "postFit_%s" % channel
canvas = ROOT.TCanvas(plotName)
legend = ROOT.TLegend(.7, .6, .95, .87)
legend.SetName(plotName+"__legend")
legend.SetNColumns(1)
# legend.SetColumnSeparation(0.1)
legend.SetFillColorAlpha(ROOT.kWhite, 0)

binningArray = array.array('d', binning)
allNumNorms = []
allNumNom = [0.]*(len(binning)-1)
allDenomNorms = []
allDenomNom = [0.]*(len(binning)-1)
tree.GetEntry(0)
for bgName in llllStack:
    pg = allPlotGroups[bgName][0]
    for iBin in range(len(binning)-1):
        binL, binH = binning[iBin:iBin+2]
        normName = "n_exp_binllll_bin%dto%d_proc_%s" % (binL, binH, pg._name)
        if not hasattr(tree, normName):
            continue
        val = getattr(tree, normName)
        allNumNom[iBin] += val
        allNumNorms.append(normName)
for bgName in lllStack:
    pg = allPlotGroups[bgName][0]
    for iBin in range(len(binning)-1):
        binL, binH = binning[iBin:iBin+2]
        normName = "n_exp_binlll_bin%dto%d_proc_%s" % (binL, binH, pg._name)
        if not hasattr(tree, normName):
            continue
        val = getattr(tree, normName)
        allDenomNom[iBin] += val
        allDenomNorms.append(normName)

mcFit = ROOT.TH1D(plotName+'__Fit', "Post-Fit MC", len(binning)-1, binningArray)
mcFit.SetLineColor(ROOT.kBlack)
mcFit.SetLineWidth(2)
mcUncertainty = ROOT.TH1D(plotName+'__FitUncertainty', "Post-Fit Uncertainty;ZZ/WZ Ratio;PF MET [GeV]", len(binning)-1, binningArray)
mcUncertainty.SetFillColor(ROOT.kGreen)
mcUncertainty.SetMarkerSize(0.)
mcUncertainty2 = ROOT.TH1D(plotName+'__FitUncertainty2', "Post-Fit Uncertainty;PF MET [GeV];ZZ/WZ Ratio", len(binning)-1, binningArray)
mcUncertainty2.SetFillColor(ROOT.kYellow)
mcUncertainty2.SetMarkerSize(0.)
mcRatios = []
mcRatioUnc = []
for iBin in range(len(binning)-1):
    binL, binH = binning[iBin:iBin+2]
    bn = '_bin%dto%d_' % (binL, binH)
    numNorms = filter(lambda n: bn in n, allNumNorms)
    denomNorms = filter(lambda n: bn in n, allDenomNorms)
    drawStr = "(%s)/(%s)" % ("+".join(numNorms), "+".join(denomNorms))
    tree.Draw(drawStr, "", "goff")
    htmp = tree.GetDirectory().Get("htemp")
    quantiles = array.array('d', [0.025, 0.16, 0.84, 0.975])
    qvals = array.array('d', [0., 0., 0., 0.])
    htmp.GetQuantiles(4, qvals, quantiles)
    l2, l, h, h2 = tuple(qvals)
    print "MC mean bin %d: " % iBin, htmp.GetMean(), htmp.GetStdDev()
    mcRatios.append(htmp.GetMean())
    mcRatioUnc.append(htmp.GetStdDev())
    print "MC unc bin %d: %f to %f" % (iBin, l, h)
    mcFit.SetBinContent(iBin+1, allNumNom[iBin]/allDenomNom[iBin])
    mcUncertainty.SetBinContent(iBin+1, (h+l)/2.)
    mcUncertainty.SetBinError(iBin+1, (h-l)/2.)
    mcUncertainty2.SetBinContent(iBin+1, (h2+l2)/2.)
    mcUncertainty2.SetBinError(iBin+1, (h2-l2)/2.)
legend.AddEntry(mcFit, mcFit.GetTitle(), 'l')
mcUncertainty2.Draw('E2')
mcUncertainty2.GetYaxis().SetRangeUser(0., 0.5)
mcUncertainty.Draw('E2same')
mcFit.Draw('histsame')

dataHist = ROOT.TH1D(plotName+'__Data', "Data", len(binning)-1, binningArray)
styles.copyStyle(styles.styles["Data"], dataHist)
chi2 = 0.
for iBin in range(len(binning)-1):
    binL, binH = binning[iBin:iBin+2]
    catNum = 'CMS_channel==CMS_channel::llll_bin%dto%d' % (binL, binH)
    catDenom = 'CMS_channel==CMS_channel::lll_bin%dto%d' % (binL, binH)
    valNum = data.sumEntries(catNum)
    valDenom = data.sumEntries(catDenom)
    print "Data bin %d: %d / %d" % (iBin, valNum, valDenom)
    if valDenom == 0.:
        continue
    val = valNum/valDenom
    chi2 += (val-mcRatios[iBin])**2/mcRatioUnc[iBin]**2
    dataHist.SetBinContent(iBin+1, val)
    err = math.sqrt(valNum*valDenom**2+valDenom*valNum**2)/valDenom**2
    dataHist.SetBinError(iBin+1, err)
dataHist.Draw('pex0same')
legend.AddEntry(dataHist, dataHist.GetTitle(), 'pe')

legend.Draw()

for obj in canvas.GetListOfPrimitives():
    ROOT.SetOwnership(obj, False)
canvas.GetListOfPrimitives().SetOwner(True)
plotting.drawCMSstuff(lumi=35867., grayText='#chi^{2} = %.2f' % chi2)

