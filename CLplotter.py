#!/usr/bin/env python
from ROOT import *
import os
from optparse import OptionParser
import json
from array import array

gROOT.SetBatch(1)
##########
home = os.getcwd()
def exclude(data):
    exclude_mx = ['1','150','500','1000']
    exclude_mv = ['15','10000']

    for mx in exclude_mx:
        if mx in data: data.pop(mx)
    for mv in exclude_mv:
        for _,mvlist in data.items():
            if mv in mvlist: mvlist.pop(mv) 
#####################################################################
def GetData(dir,exclude=exclude):
    data = {}
    os.chdir(dir)
    cwd = os.getcwd()
    data['lumi'] = 35900
    data['year'] = '2016'
    data['variable'] = 'ChNemPtFrac'
    with open('limits.json') as f: d_json = json.load(f)
    limits = {}
    for mx,mxinfo in d_json.iteritems():
        mxlim = {}
        for mv,mvinfo in mxinfo.iteritems():
            scale = d_json[mx][mv]['scale']
            mxlim[mv] = { exp:scale*val for exp,val in mvinfo['limits'].iteritems() }
        limits[mx] = mxlim
    exclude(limits)
    data['limit'] = limits
    os.chdir(home)
    return data
#####################################################################
def Plot2D(data):
    mxlist = sorted(data.keys(),key=int)
    mxbins = { mx:i+1 for i,mx in enumerate(mxlist) }
    mvlist = []
    for mx in mxlist:
        for mv in sorted(data[mx],key=float):
            if mv not in mvlist: mvlist.append(mv); mvlist.sort(key=float)
    mvbins = { mv:i+1 for i,mv in enumerate(mvlist) }
    xbins = len(mvlist); ybins = len(mxlist)
    limit = TH2D("Expected Limits","",xbins,0,xbins,ybins,0,ybins)
    for mx in mxlist:
        for mv in data[mx]:
            limit.SetBinContent(mvbins[mv],mxbins[mx],data[mx][mv]['exp0'])
    return limit,mxlist,mvlist
#######################################################################
def drawPlot2D(data):
    print 'Plotting 2D'
    lumi = data['lumi']
    data = data['limit']
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
    texS1 = TLatex(0.15,0.93,"#bf{CMS} : #it{Preliminary} (2016)");
    texS1.SetNDC();
    texS1.SetTextFont(42);
    texS1.SetTextSize(0.035);
    texS1.Draw();
    ################################################################
    c.Modified()
    c.Update()
    c.SaveAs("expectedevents2D.png")
    # c.SaveAs("expectedevents2D.pdf")
#####################################################################
def Plot1D(data):
    mxlist = sorted(data.keys(),key=int)
    limits = {}
    for mx in mxlist:
        xlist = []; ylist = []
        for i,mv in enumerate( sorted(data[mx],key=float) ):
            x = float(mv); y = data[mx][mv]['exp0']
            xlist.append(x); ylist.append(y)
        xlist = array('d',xlist); ylist = array('d',ylist);
        limits[mx] = TGraph(len(xlist),xlist,ylist)
    return limits,mxlist
#####################################################################
def drawPlot1D(data):
    print 'Plotting 1D'
    lumi = data['lumi']
    data = data['limit']
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
    texS1 = TLatex(0.12092,0.907173,"#bf{CMS} : #it{Preliminary}");
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
    c.SaveAs("expectedevents1D.png")
#####################################################################

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d","--dir",help='Specify the directory to read limits from',action='store',type='str',default=None)
    parser.add_option("-v","--version",help='Specify the version of plot (1D or 2D)',action='store',type='str',default='2D')
    options,args = parser.parse_args()
    if options.dir == None:
        print "Please specify a director to run limits in."
        exit()
    if options.version != '1D' and options.version != '2D':
        print 'Unkown plot version,',options.version+'.'
        print 'Plotting Default 2D Plot.'
        options.version = '2D'
    data = GetData(options.dir)
    if   options.version == '1D': drawPlot1D(data)
    elif options.version == '2D': drawPlot2D(data)

