from ROOT import *

def getLegend(xmin=0.5,ymin=0.65,xmax=0.7,ymax=0.887173):
    leg = TLegend(xmin,ymin,xmax,ymax,"")
    leg.SetFillColor(kWhite);
    leg.SetFillStyle(0);
    leg.SetTextSize(0.025);
    return leg
def getCMSText(year):
    x1,y1 = 0.62,0.907173
    texS = TLatex(x1,y1,("XX fb^{-1} (13 TeV, %s)" % year));#VS
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.040);
    texS.Draw();

    x2,y2 = 0.15,0.837173
    texS1 = TLatex(x2,y2,"#bf{CMS} #it{Preliminary}"); 
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.040);
    texS1.Draw();
    return texS,texS1
def data_style(graph):
    graph.SetTitle("")
    graph.SetMarkerStyle(20)
def fit_style(hs,color):
    hs.SetTitle("")
    hs.GetYaxis().SetTitle("Events")
    hs.SetLineColor(color)
    hs.SetLineWidth(2)
    hs.SetFillStyle(0)
    hs.SetFillColor(0)
def set_bounds(hs):
    ymin = min( hs[ibin] for ibin in range(1,hs.GetNbinsX()+1) if hs[ibin] != 0)
    ymax = max( hs[ibin] for ibin in range(1,hs.GetNbinsX()+1) if hs[ibin] != 0)

    hs.SetMinimum(0.05)
    hs.SetMaximum(ymax*(10**2.5))
def ratio_style(ratio,color,rymin=0.65,rymax=1.35):
    gPad.SetGridy();
    ratio.SetMarkerStyle(20)
    ratio.SetMarkerColor(color)
    ratio.SetTitle("")
    ratio.GetYaxis().SetRangeUser(rymin,rymax);
    ratio.SetStats(0);
    ratio.GetYaxis().CenterTitle();
    ratio.GetYaxis().SetTitle("Data/MC")
    ratio.SetMarkerStyle(20);
    ratio.SetMarkerSize(1);
    ratio.GetYaxis().SetLabelSize(0.1);
    ratio.GetYaxis().SetTitleSize(0.1);
    ratio.GetYaxis().SetLabelFont(42);
    ratio.GetYaxis().SetTitleFont(42);
    ratio.GetYaxis().SetTitleOffset(0.35);
    ratio.GetYaxis().SetNdivisions(4);
    ratio.GetYaxis().SetTickLength(0.05);
    
    ratio.GetXaxis().SetLabelSize(0.1);
    ratio.GetXaxis().SetTitleSize(0.1);
    ratio.GetXaxis().SetLabelFont(42);
    ratio.GetXaxis().SetTitleFont(42);
    ratio.GetXaxis().SetTitleOffset(1.2);
    ratio.GetXaxis().SetTickLength(0.05);
def makeHistogram(graph,template):
    hs = template.Clone();
    npoints = graph.GetN()
    for i in range(npoints):
        x,y=Double(0),Double(0)
        graph.GetPoint(i,x,y)
        xerr = graph.GetErrorX(i)
        yerr = graph.GetErrorY(i)
        hs.SetBinContent(i+1,y)
        hs.SetBinError(i+1,yerr)
    return hs;
