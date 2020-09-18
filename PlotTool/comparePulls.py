import sys
from ROOT import *
from PlotTool import *
from array import array
from argparse import ArgumentParser
from math import ceil

gROOT.SetBatch(1)

def DiffGraph(g1,g2):
    diff = g1.Clone();
    for i in range(diff.GetN()):
        x1,x2,y1,y2 = Double(),Double(),Double(),Double()
        g1.GetPoint(i,x1,y1); g2.GetPoint(i,x2,y2)
        e1 = g1.GetErrorY(i); e2 = g2.GetErrorY(i)
        e = TMath.Sqrt( e1**2 + e2**2 )
        diff.SetPoint(i,x1,y1-y2)
        diff.SetPointError(i,0,0,e,e)
    return diff
class Pulls(TFile):
    def __init__(self,*args,**kwargs):
        TFile.__init__(self,*args,**kwargs)

        label = self.GetName().split("/")[1]
        canvas = self.Get("nuisances")
        objlist = canvas.GetListOfPrimitives()
        self.prefit = objlist.At(0).Clone()
        self.fit_bg = objlist.At(2).Clone(label)
        self.fit_bs = objlist.At(3).Clone()
        # self.legend = objlist.At(6).Clone()

        def get_graph_point(graph,point):
            x,y = Double(),Double()
            graph.GetPoint(point,x,y)
            return (float(y),graph.GetErrorY(point))

        self.nuisances = {}
        for ibin in range(1,self.prefit.GetNbinsX()+1):
            nuisance = self.prefit.GetXaxis().GetBinLabel(ibin)
            self.nuisances[nuisance] = {
                "name":nuisance,
                "prefit":(self.prefit.GetBinContent(ibin),self.prefit.GetBinError(ibin)),
                "fit_bg":get_graph_point(self.fit_bg,ibin-1),
                "fit_bs":get_graph_point(self.fit_bs,ibin-1),
            }
    def get(self,nuisances):
        def Clone(tobj):
            obj = tobj.Clone()
            if tobj.ClassName() == "TH1F": obj.Reset()
            if tobj.ClassName() == "TGraphAsymmErrors": obj.Set(len(nuisances))
            return obj
        prefit = Clone(self.prefit)
        fit_bg = Clone(self.fit_bg)
        fit_bs = Clone(self.fit_bs)
        for i,nuisance in enumerate(iter( self.nuisances[nuisance] for nuisance in nuisances )):
            label = nuisance["name"]
            val1,err1 = nuisance["prefit"]
            (y1,ey1) = nuisance["fit_bg"]
            (y2,ey2) = nuisance["fit_bs"]
            prefit.SetBinContent(i+1,val1)
            prefit.SetBinError(i+1,err1)
            prefit.GetXaxis().SetBinLabel(i+1,label)
            fit_bg.SetPoint(i,i+0.6,y1)
            fit_bg.SetPointError(i,0,0,ey1,ey1)
            
            fit_bs.SetPoint(i,i+0.4,y2)
            fit_bs.SetPointError(i,0,0,ey2,ey2)

        return prefit,fit_bg,fit_bs
        
parser = ArgumentParser()
parser.add_argument("pulls",help="List of pull files, first one used as nominal",nargs="*",type=Pulls)
parser.add_argument("-npull",help="Number of pulls per page",default=10,type=int)
parser.add_argument("-o","--output",default="compare_pulls.pdf")

args = parser.parse_args()

def sort_nicely( l ):
    """ Sort the given list in the way that humans expect.
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )
    return l
def GetNuisances(pulls):
    nuisances = [ set(pull.nuisances.keys()) for pull in pulls ]
    likenuis = None
    for nuisance in nuisances:
        if likenuis is None: likenuis = nuisance
        likenuis = likenuis.intersection(nuisance)
    statnuis = [ nuis for nuis in likenuis if "stat" in nuis ]
    sysnuis = [ nuis for nuis in likenuis if "stat" not in nuis ]
    return sort_nicely(sysnuis) + sort_nicely(statnuis)

nuisances = GetNuisances(args.pulls)
print "Plotting %s Nuisances" % len(nuisances)
plotlist = [ pull.get(nuisances) for pull in args.pulls ]
diff_pulls = [ DiffGraph(plotlist[0][1],fit_bg) for (prefit,fit_bg,fit_bs) in plotlist[1:] ]

colorlist = [kBlack,kRed,kGreen+2,kBlue]

def ShiftGraph(graph,shift):
    x,y = Double(),Double()
    for i in range(graph.GetN()):
        graph.GetPoint(i,x,y)
        graph.SetPoint(i,float(x) + shift,float(y))
        
shift = lambda x : -0.3 + 0.4 * x/float(len(plotlist)-1)
for i,(prefit,fit_bg,fit_bs) in enumerate(plotlist):
    color = colorlist[i]
    fit_bg.SetMarkerColor(color)
    fit_bg.SetLineColor(color)
    ShiftGraph(fit_bg,shift(i))

shift = lambda x : -0.3 + 0.4 * x/float(len(diff_pulls)-1)
for i,diff in enumerate(diff_pulls): 
    color = colorlist[i+1]
    diff.SetMarkerColor(color)
    diff.SetLineColor(color)
    ShiftGraph(diff,shift(i))
    
def GetPage(page,npages):
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    canvas = TCanvas()
    canvas.SetGridx()
    canvas.Divide(1,2)

    xlo = page * args.npull + 1
    xhi = page * args.npull + args.npull
    if xhi > len(nuisances): xhi = len(nuisances)

    pad1 = canvas.cd(1)
    pad1.SetGridx()
    pad1.SetBottomMargin(0)
    n_prefit,_,_ = plotlist[0]
    n_prefit.GetXaxis().SetRange(xlo,xhi)
    n_prefit.GetYaxis().SetRangeUser(-4,4)
    n_prefit.Draw("E2")
    n_prefit.Draw("histsame")

    for i,(prefit,fit_bg,fit_bs) in enumerate(plotlist):
        fit_bg.Draw("EP same")
    legend = pad1.BuildLegend()
    legend.Clear()
    for prefit,fit_bg,fit_bs in plotlist:
        legend.AddEntry(fit_bg,fit_bg.GetName(),"pl")
    legend.Draw()

    pad2 = canvas.cd(2)
    pad2.SetGridx()
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.5)
    diff_prefit = n_prefit.Clone()
    diff_prefit.SetTitle("")
    diff_prefit.GetYaxis().SetTitle("Diff Pulls to %s"%plotlist[0][1].GetName())
    # diff_prefit.GetYaxis().SetTitleSize(0.08)
    diff_prefit.GetXaxis().SetLabelSize(0.07);
    diff_prefit.Draw("E2")
    diff_prefit.Draw("histsame")
    
    for i,diff in enumerate(diff_pulls):
        diff.Draw("EP same")

    if page == 0: canvas.SaveAs(args.output+"(")
    elif page+1 == npages: canvas.SaveAs(args.output+")")
    else: canvas.SaveAs(args.output)

npages = int(ceil(float(len(nuisances))/args.npull))
for page in range(npages): GetPage(page,npages)
    
