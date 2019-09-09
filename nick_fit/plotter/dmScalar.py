#!/usr/bin/env python
import ROOT
import array
import glob
import sys
import math
import plotting

ROOT.gStyle.SetOptDate(False)
plotting.styles.forceStyle()


def getLimits(fn):
    # Use example:
    # exp_m2s, exp_m1s, exp, exp_p1s, exp_p2s, obs = getLimits("higgsCombineTest.Asymptotic.mH120.root")
    lim = []
    f = ROOT.TFile.Open(fn)
    tree = f.Get("limit")
    for i in range(6):
        tree.GetEntry(i)
        lim.append(tree.limit)
    return tuple(lim)


# S or P
med = sys.argv[-1]
plotName = "limit_pseudo" if med == 'P' else "limit_scalar"

pointFiles = glob.glob("result/0j%s/*/higgsCombineTest.Asymptotic.mH120.root" % med)
limits = []
for fn in pointFiles:
    mx, mv = map(int, fn.split('/')[2].split('_'))
    if mv == 0:
        print "Skipping %s" % fn
        continue
    limit = (mv, ) + getLimits(fn)
    if limit[-1] <= 0.:
        print "Problem in %s, skipping" % fn
        continue
    limits.append(limit)


limits.sort()
nPoints = len(limits)
# mv, exp_m2s, exp_m1s, exp, exp_p1s, exp_p2s, obs
limit_x   = array.array("d", [l[0] for l in limits])
limit_obs = array.array("d", [l[6] for l in limits])
limit_exp = array.array("d", [l[3] for l in limits])
limit_m1s = array.array("d", [l[3]-l[2] for l in limits])
limit_p1s = array.array("d", [l[4]-l[3] for l in limits])
limit_m2s = array.array("d", [l[3]-l[1] for l in limits])
limit_p2s = array.array("d", [l[5]-l[3] for l in limits])
dummy = array.array("d", [0.]*len(limits))

c = ROOT.TCanvas(plotName, "canvas")
c.SetLogy(True)

graph_2sd = ROOT.TGraphAsymmErrors(nPoints, limit_x, limit_exp, dummy, dummy, limit_m2s, limit_p2s)
graph_2sd.SetNameTitle("graph_2sd", "Expected #pm 2 s.d.")
graph_2sd.SetFillColor(ROOT.kOrange)
graph_2sd.Draw("a3")
graph_2sd.GetXaxis().SetTitle("#it{m}_{med} [GeV]")
graph_2sd.GetYaxis().SetTitle("#sigma_{obs}/#sigma_{theo}")
graph_2sd.GetYaxis().SetRangeUser(1e-1, 1e4)

graph_1sd = ROOT.TGraphAsymmErrors(nPoints, limit_x, limit_exp, dummy, dummy, limit_m1s, limit_p1s)
graph_1sd.SetNameTitle("graph_1sd", "Expected #pm 1 s.d.")
graph_1sd.SetFillColor(ROOT.kGreen+1)
graph_1sd.Draw("3")

graph_exp = ROOT.TGraph(nPoints, limit_x, limit_exp)
graph_exp.SetNameTitle("graph_exp", "Expected 95% CL")
graph_exp.SetLineColor(ROOT.kBlack)
graph_exp.SetLineStyle(ROOT.kDashed)
graph_exp.SetMarkerColor(ROOT.kBlack)
graph_exp.SetMarkerStyle(ROOT.kOpenCircle)
graph_exp.Draw("pl")

graph_obs = ROOT.TGraph(nPoints, limit_x, limit_obs)
graph_obs.SetNameTitle("graph_obs", "Observed 95% CL")
graph_obs.SetLineColor(ROOT.kBlack)
graph_obs.SetMarkerColor(ROOT.kBlack)
graph_obs.SetMarkerStyle(ROOT.kFullCircle)
graph_obs.Draw("pl")

legend = ROOT.TLegend(.6, .2, .95, .4)
legend.SetFillColorAlpha(ROOT.kWhite, 1.)
legend.AddEntry(graph_exp, graph_exp.GetTitle(), "lp")
legend.AddEntry(graph_1sd, graph_1sd.GetTitle(), "f")
legend.AddEntry(graph_2sd, graph_2sd.GetTitle(), "f")
legend.AddEntry(graph_obs, graph_obs.GetTitle(), "lp")
legend.Draw()

typetext = ROOT.TLatex()
typetext.SetNDC()
typetext.SetX(ROOT.gPad.GetLeftMargin()+0.04)
typetext.SetY(0.78)
typetext.SetTextAlign(13)
typetext.SetTextSize(0.03)
typetext.SetTextFont(42)
type = "Pseudoscalar" if med == 'P' else "Scalar"
typetext.SetTitle("#splitline{"+type+" mediator, #it{g}_{q} = 1.0}{Dirac DM, #it{m}_{DM} = 1 GeV, #it{g}_{DM} = 1.0}")
typetext.Draw()


plotting.drawCMSstuff(lumi=35867., grayText='', type=2)
c.Print(plotName+".pdf")
c.Print(plotName+".root")
