#!/usr/bin/env python
import ROOT
import glob
import sys
import math
import plotting

ROOT.gStyle.SetOptDate(False)
plotting.styles.forceStyle()
ROOT.gStyle.SetNumberContours(100)
# ROOT.gStyle.SetPalette(ROOT.kTemperatureMap)
ROOT.gStyle.SetPalette(ROOT.kLightTemperature)
add = 3
ROOT.gStyle.SetPadRightMargin(0.04*(1+add))
ROOT.gStyle.SetCanvasDefW(int(600*(1+0.04*add)))


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


def buildContour(graph2d, nPoints=200, startPosition=(300., 1.), phiBounds=(math.pi, 0.), muTarget=1.):
    def getXY(r, phi):
        px, py = startPosition
        px += r*math.cos(phi)
        py += r*math.sin(phi)
        return (px, py)

    contour = ROOT.TGraph(nPoints)
    contour.SetLineWidth(2)
    for i in xrange(nPoints):
        phi = i*(phiBounds[1]-phiBounds[0])/float(nPoints-1) + phiBounds[0]
        r = 1.
        val = graph2d.Interpolate(*getXY(r, phi))
        while val-muTarget < 0. and val > 0. and r < 500.:
            r += 0.1
            val = graph2d.Interpolate(*getXY(r, phi))
        contour.SetPoint(i, *getXY(r, phi))

    return contour


def dumpTGraph(gr, filename):
    with open(filename, "w") as fout:
        x, y = ROOT.Double(), ROOT.Double()
        for i in xrange(gr.GetN()):
            gr.GetPoint(i, x, y)
            fout.write(str(x)+" "+str(y)+"\n")

# A or V
med = sys.argv[-1]
plotName = "limit_axial" if med == 'A' else "limit_vector"

fs_pts = [(20,0), (10000,1000), (1000,1000), (300,100), (750,100), (10000,10), (100,10), (10,10), (50,10), (300,140), (10000,150), (1000,150), (200,150), (500,150), (10000,1), (1000,1), (100,1), (10,1), (2000,1), (200,1), (300,1), (500,1), (50,1), (750,1), (750,200), (750,300), (100,40), (1000,490), (10000,500), (2000,500), (500,500), (200,50), (300,50), (500,50), (50,50), (1000,75), (500,75), (2000,990) ]

iPoint = 0
limit_obs = []
limit_exp = []
limit_m1s = []
limit_p1s = []
for fn in glob.glob("result/NLO%s/*/higgsCombineTest.Asymptotic.mH120.root" % med):
    mx, mv = map(int, fn.split('/')[2].split('_'))
    if mv == 0:
        print "Skipping %s" % fn
        continue
    if (mv, mx) in fs_pts and mv > 20:
        print "Skipping fullsim point %s" % fn
        continue
    exp_m2s, exp_m1s, exp, exp_p1s, exp_p2s, obs = getLimits(fn)
    if obs <= 0.:
        print "Problem in %s, skipping" % fn
        continue
    iPoint += 1
    # y = float(mx)
    y = 2*float(mx)/mv
    limit_obs.append((iPoint, mv, y, obs))
    limit_exp.append((iPoint, mv, y, exp))
    limit_m1s.append((iPoint, mv, y, exp_m1s))
    limit_p1s.append((iPoint, mv, y, exp_p1s))

def makeGraph(pts, name, title, resampleTransformed=True):
    if resampleTransformed:
        gtmp = ROOT.TGraph2D(len(pts))
        gtmp.SetName("tmptmp")
        for p in pts:
            gtmp.SetPoint(*p)
        npx, npy = 100, 100
        new_pts = []
        for i in xrange(npx):
            xval = i*1000./float(npx-1)
            for j in xrange(npy):
                yval = j*500./float(npy-1)
                if yval*2./max(xval, 1.) > 1.49:
                    continue
                new_pts.append((xval, yval, gtmp.Interpolate(xval, yval*2./max(xval, 1.))))
        g = ROOT.TGraph2D(len(new_pts))
        for i, p in enumerate(new_pts):
            g.SetPoint(i, *p)
        g.SetName(name)
        g.SetTitle(title)
        del gtmp
    else:
        g = ROOT.TGraph2D(len(pts))
        for p in pts:
            g.SetPoint(*p)
        g.SetName(name)
        g.SetTitle(title)
    return g

# Transformed space
limit_obs_trans = makeGraph(limit_obs, "limit_obs_trans", "nolegend", resampleTransformed=False)
h_limit_obs_trans = ROOT.TH2D("h_limit_obs_trans",";#it{M_{med}} [GeV];#it{2*M_{#chi}/M_{med}} [GeV];95% CL observed limit on #sigma_{obs}/#sigma_{theo}",100,0,1000,100,0,2)
limit_obs_trans.SetHistogram(h_limit_obs_trans)

# 2D (only observed gets used except for finding the contours)
limit_obs = makeGraph(limit_obs, "limit_obs", "nolegend")
limit_exp = makeGraph(limit_exp, "limit_exp", "nolegend")
limit_m1s = makeGraph(limit_m1s, "limit_m1s", "nolegend")
limit_p1s = makeGraph(limit_p1s, "limit_p1s", "nolegend")

h_limit_obs = ROOT.TH2D("h_limit_obs",";#it{m}_{med} [GeV];#it{m}_{DM} [GeV];95% CL observed limit on #sigma_{obs}/#sigma_{theo}",200,0,1000,200,0,500)
limit_obs.SetHistogram(h_limit_obs)

# Delaunay triangulation grid
c = ROOT.TCanvas(plotName, "canvas")
c.SetTheta(90.)
c.SetPhi(0.01)
limit_obs.Draw("triw")
c.Print(plotName+"_grid.pdf")
c.Clear()
limit_obs_trans.Draw("triw")
c.Print(plotName+"_trans_grid.pdf")
c.Clear()
_ = limit_obs_trans.GetHistogram("colz")
h_limit_obs_trans.GetZaxis().SetRangeUser(0.01, 100)
h_limit_obs_trans.Draw("colz")
c.SetLogz(True)
c.Print(plotName+"_trans.pdf")
c.Clear()

legend = ROOT.TLegend(.52, .71, .81, .90)
legend.SetFillColorAlpha(ROOT.kWhite, 1.)
legend.SetBorderSize(1)
legend.SetLineWidth(1)
legend.SetLineColorAlpha(ROOT.kBlack, 0.5)
legend.SetHeader("#sigma/#sigma_{theo} = 1")
def quickAdd(h):
    legend.AddEntry(h, h.GetTitle(), h.GetDrawOption())

# Force filling the hist with interpolation
# (returns pointer to h_limit_obs)
_ = limit_obs.GetHistogram("colz")
h_limit_obs.GetZaxis().SetRangeUser(0.01, 100)
h_limit_obs.Draw("colz")
c.SetLogz(True)

contour_obs = buildContour(limit_obs, nPoints=1000)
dumpTGraph(contour_obs, plotName+"_observed.txt")
contour_obs.SetNameTitle("contour_obs", "Observed")
contour_obs.SetLineColor(ROOT.kRed)
contour_obs.Draw("l")
quickAdd(contour_obs)

contour_obs_theop = buildContour(limit_obs, muTarget=1.05)
contour_obs_theop.SetNameTitle("contour_obs_theop", "Theory Uncertainty")
contour_obs_theop.SetLineColor(ROOT.kRed)
contour_obs_theop.SetLineStyle(ROOT.kDashed)
contour_obs_theop.Draw("l")
quickAdd(contour_obs_theop)

contour_obs_theom = buildContour(limit_obs, muTarget=0.95)
contour_obs_theom.SetNameTitle("contour_obs_theom", "nolegend")
contour_obs_theom.SetLineColor(ROOT.kRed)
contour_obs_theom.SetLineStyle(ROOT.kDashed)
contour_obs_theom.Draw("l")

contour_exp = buildContour(limit_exp)
dumpTGraph(contour_exp, plotName+"_expected.txt")
contour_exp.SetNameTitle("contour_exp", "Expected")
contour_exp.SetLineColor(ROOT.kBlack)
contour_exp.Draw("l")
quickAdd(contour_exp)

contour_exp_p1s = buildContour(limit_p1s)
contour_exp_p1s.SetNameTitle("contour_exp_p1s", "Expected #pm 1 s.d.")
contour_exp_p1s.SetLineColor(ROOT.kBlack)
contour_exp_p1s.SetLineStyle(ROOT.kDashed)
contour_exp_p1s.Draw("l")
quickAdd(contour_exp_p1s)

contour_exp_m1s = buildContour(limit_m1s)
contour_exp_m1s.SetNameTitle("contour_exp_m1s", "nolegend")
contour_exp_m1s.SetLineColor(ROOT.kBlack)
contour_exp_m1s.SetLineStyle(ROOT.kDashed)
contour_exp_m1s.Draw("l")

# Add relic density
def relicStyle(graph):
    graph.SetLineColor(ROOT.kAzure+3)
    graph.SetLineStyle(1)
    graph.SetLineWidth(402)
    graph.SetFillStyle(3005)
    graph.SetFillColor(ROOT.kAzure+3)
fRelic = ROOT.TFile.Open("relic_%s1.root" % med)
relic1 = fRelic.Get("mytlist").First()
relicStyle(relic1)
relic1.SetNameTitle("relic1", "#Omega_{c}h^{2} #geq 0.12")
relic1.Draw("l")
legend.AddEntry(relic1, relic1.GetTitle(), 'f')
if med == 'A':
    relic2 = fRelic.Get("mytlist").Last()
    relic2.SetNameTitle("relic2", "relic2")
    relic2.Draw("l")

legend.Draw()

typetext = ROOT.TLatex()
typetext.SetNDC()
typetext.SetX(ROOT.gPad.GetLeftMargin()+0.04)
typetext.SetY(0.78)
typetext.SetTextAlign(13)
typetext.SetTextSize(0.03)
typetext.SetTextFont(42)
type = "Axial-vector" if med == 'A' else "Vector"
typetext.SetTitle("#splitline{"+type+" mediator, g_{q} = 0.25}{Dirac DM, g_{DM} = 1}")
typetext.Draw()


plotting.drawCMSstuff(lumi=35867., grayText='', type=1)
c.Print(plotName+".pdf")
c.Print(plotName+".root")

delaunay = limit_exp.GetHistogram("empty").GetListOfFunctions().First()
triangles = [(delaunay.begin()+i).__deref__() for i in xrange(delaunay.GetNdt())]
