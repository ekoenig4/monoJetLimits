#!/usr/bin/env python
from ROOT import *
import os
from argparse import ArgumentParser
import json
from array import array
from PlotTool import *
import re

gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"
home = os.getcwd()
def checkdir(dir):
    if not os.path.isdir(dir): os.mkdir(dir)
#####################################################################
def exclude(data):
    exclude_mx = ['1','150','500','1000']
    exclude_mx = []
    exclude_mv = ['15','10000']

    for mx in exclude_mx:
        if mx in data: data.pop(mx)
    for mv in exclude_mv:
        for _,mvlist in data.items():
            if mv in mvlist: mvlist.pop(mv) 
#####################################################################
def drawPlot2D(data):
    print 'Plotting 2D'
    lumi = data.lumi
    year = data.year
    variable = data.variable
    cut = data.cut
    extra = data.extra
    limit,mxlist,mvlist = Plot2D(data)
    xbins = len(mvlist)
    ybins = len(mxlist)
    ######################################################################
    c = TCanvas("c","c",800,800)
    c.SetMargin(0.15,0.15,0.15,0.08)
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    gStyle.SetPaintTextFormat("4.3f")

    limit.Draw('COLZ TEXT89')
    limit.SetStats(0)
    
    limit.GetXaxis().SetTitleOffset(999)
    limit.GetXaxis().SetLabelOffset(999)
    limit.GetXaxis().SetTickLength(0)

    limit.GetYaxis().SetTitleOffset(999)
    limit.GetYaxis().SetLabelOffset(999)
    limit.GetYaxis().SetTickLength(0)

    limit.GetZaxis().SetTitle("95% CL limit on #sigma/#sigma_{theory}")
    limit.GetZaxis().SetTitleOffset(1.2)
    ########################################################################
    xaxis = TGaxis(0,0,xbins,0,0,xbins,xbins)
    xaxis.SetTitle("m_{med} [GeV]")
    xaxis.SetLabelFont(42);
    xaxis.SetLabelSize(0);
    xaxis.SetTitleFont(42);
    xaxis.SetTitleSize(0.05);
    xaxis.SetTitleOffset(0.9);
    xaxis.Draw("SAME")

    label=TLatex()
    label.SetTextSize(0.015);
    label.SetTextFont(42)
    
    for i,mv in enumerate(mvlist):
        size=float(len(mv))
        label.DrawLatex(i+0.5/size,-0.08,str(int(float(mv))))

    yaxis = TGaxis(0,0,0,ybins,0,ybins,ybins)
    yaxis.SetTitle("m_{#chi} [GeV]")
    yaxis.SetLabelFont(42);
    yaxis.SetLabelSize(0);
    yaxis.SetTitleFont(42);
    yaxis.SetTitleSize(0.05);
    # yaxis.SetTitleOffset(1.2);
    yaxis.Draw("SAME")

    label.SetTextSize(0.04);
    for i,mx in enumerate(mxlist):
        size=len(mx)
        label.DrawLatex(-0.5*size,i+0.5,mx)
    ################################################################
    lumi_label = '%s' % float('%.3g' % (lumi/1000.)) + " fb^{-1}"
    texS = TLatex(0.55,0.93,("#sqrt{s} = 13 TeV, "+lumi_label));
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.035);
    texS.Draw();
    texS1 = TLatex(0.15,0.93,"#bf{CMS} : #it{Preliminary} (%s)" % year);
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.035);
    texS1.Draw();
    ################################################################
    c.Modified()
    c.Update()

    outdir = outdir_base % year
    checkdir(outdir)
    subdir = variable
    outdir += '/%s' % subdir
    checkdir(outdir)
    fname = '%s%s_%s2D.png' % (variable,cut,''.join(extra))
    c.SaveAs( '%s/%s' % (outdir,fname) )
#####################################################################
def drawPlot1D(data):
    print 'Plotting 1D'
    lumi = data.lumi
    year = data.year
    variable = data.variable
    cut = data.cut
    extra = data.extra
    plots,mxlist = Plot1D(data)

    maxX = max( max( float(mv) for mv in mvlist ) for mx,mvlist in data.items() )
    minX = min( min( float(mv) for mv in mvlist ) for mx,mvlist in data.items() )
    maxY = max( max( lim['exp0'] for mv,lim in mvlist.items() ) for mx,mvlist in data.items() )
    minY = min( min( lim['exp0'] for mv,lim in mvlist.items() ) for mx,mvlist in data.items() )
    ######################################################################
    c = TCanvas("c","c",800,800)
    c.SetLogy()
    # c.SetMargin(0.15,0.15,0.15,0.08)
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    # gStyle.SetPalette(kRainBow)

    limits = TMultiGraph()
    legend = TLegend(0.4,0.65,0.65,0.82,"")
    legend.SetTextSize(0.02)
    legend.SetFillColor(0)
    for mx in mxlist:
        limit = plots[mx]
        legend.AddEntry(limit,'m_{#chi} = '+mx+' GeV','l')
        limit.SetLineWidth(3)
        limits.Add(limit)
    limits.Draw('a l plc')
    limits.GetXaxis().SetRangeUser(minX,maxX)
    limits.GetYaxis().SetRangeUser(minY*(10**-0.2),maxY*(10**1))
    limits.GetXaxis().SetTitle("m_{med} (GeV)")
    limits.GetYaxis().SetTitle("95% CL limit on #sigma/#sigma_{theor}")
    limits.GetXaxis().SetTitleSize(0.04)
    limits.GetYaxis().SetTitleSize(0.04)
    limits.GetXaxis().SetTitleOffset(0.92)
    limits.GetYaxis().SetTitleOffset(0.92)
    limits.GetXaxis().SetLabelSize(0.03)
    limits.GetYaxis().SetLabelSize(0.03)
    ################################################################

    lumi_label = '%s' % float('%.3g' % (lumi/1000.)) + " fb^{-1}"
    texS = TLatex(0.20,0.837173,("#sqrt{s} = 13 TeV, "+lumi_label));
    texS.SetNDC();
    texS.SetTextFont(42);
    texS.SetTextSize(0.040);
    texS.Draw('same');
    texS1 = TLatex(0.12092,0.907173,"#bf{CMS} : #it{Preliminary} (%s)" % year);
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.040);
    texS1.Draw('same');

    legend.Draw('same')

    line = TLine(minX,1,maxX,1)
    line.SetLineStyle(8)
    line.Draw('same')
    
    c.Modified()
    c.Update()

    outdir = outdir_base % year
    checkdir(outdir)
    subdir = variable
    outdir += '/%s' % subdir
    checkdir(outdir)
    fname = '%s%s_%s1D.png' % (variable,cut,''.join(extra))
    c.SaveAs( '%s/%s' % (outdir,fname) )
#####################################################################
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        else: raise ValueError('Directories only')
    def version(arg):
        if '1D' in arg or '2D' == arg:  return arg
        else:  return None
    parser = ArgumentParser(description="Plot limit information from specified directory")
    parser.add_argument("-d","--dir",help='Specify the directory to read limits from',action='store',type=directory,default=None,required=True)
    parser.add_argument("-v","--version",help='Specify the version of plot (1D or 2D)',action='store',type=version,default=None)
    try: arg = parser.parse_args()
    except:
        parser.print_help()
        exit()
    return parser.parse_args()
#####################################################################
if __name__ == "__main__":
    args = getargs()
    if args.dir == None:
        print "Please specify a director to run limits in."
        exit()
    if args.version == None: version = ('1D','2D')
    else:  version = (args.version,)
    data = Limits(args.dir)
    for ver in version:
        if   ver == '1D': drawPlot1D(data)
        elif ver == '2D': drawPlot2D(data)

