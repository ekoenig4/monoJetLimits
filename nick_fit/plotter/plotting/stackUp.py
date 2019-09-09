# Makes the generic stack of datasets plot
import ROOT
from PlotGroup import PlotGroup
import styles


def stackUp(plotGroups, plotName, callback=None):
    canvas = ROOT.TCanvas(plotName)
    legend = ROOT.TLegend(.7, .6, .95, .87)
    legend.SetName(plotName+"__legend")
    legend.SetNColumns(1)
    # legend.SetColumnSeparation(0.1)
    legend.SetFillColorAlpha(ROOT.kWhite, 0)

    mcPlotGroups = filter(lambda g: g.plotType() == PlotGroup.Stackable, plotGroups)
    if len(mcPlotGroups) > 0:
        mcStack = ROOT.THStack(plotName+'__stack', 'Stack')
        mcUncertainty = None
        for group in mcPlotGroups:
            hist = group.getPlot(plotName, callback)
            mcStack.Add(hist, "hist")
            legend.AddEntry(hist, hist.GetTitle(), 'f')
            ROOT.SetOwnership(hist, False)
            if mcUncertainty:
                mcUncertainty.Add(hist)
            else:
                mcUncertainty = hist.Clone(plotName+'__stackUncertainty')
                mcUncertainty.SetTitle('MC Uncertainty')

        mcStack.Draw()
        mcStack.SetMaximum(mcStack.GetMaximum()*1.5)
        mcStack.GetXaxis().SetTitle(mcUncertainty.GetXaxis().GetTitle())
        mcStack.GetYaxis().SetTitle(mcUncertainty.GetYaxis().GetTitle())

        styles.copyStyle(styles.styles["MCUncertainty"], mcUncertainty)
        mcUncertainty.Draw('E2same')

    signalPlotGroups = filter(lambda g: g.plotType() == PlotGroup.SignalLike, plotGroups)
    for i, sig in enumerate(signalPlotGroups):
        sigHist = sig.getPlot(plotName, callback)
        if not sig.hasStyle():
            styles.copyStyle(styles.styles["Signal%d" % i], sigHist)
        sigHist.Draw('histex0same')
        ROOT.SetOwnership(sigHist, False)
        legend.AddEntry(sigHist, sigHist.GetTitle(), 'le')

    dataPlotGroups = filter(lambda g: g.plotType() == PlotGroup.Data, plotGroups)
    if len(dataPlotGroups) == 1:
        dataHist = dataPlotGroups[0].getPlot(plotName, callback)
        dataHist.Draw('pex0same')
        ROOT.SetOwnership(dataHist, False)
        legend.AddEntry(dataHist, dataHist.GetTitle(), 'pe')

    legend.Draw()

    for obj in canvas.GetListOfPrimitives():
        ROOT.SetOwnership(obj, False)
    canvas.GetListOfPrimitives().SetOwner(True)
    return canvas
