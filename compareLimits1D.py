from ROOT import *
import os
from optparse import OptionParser
from array import array
from CLplotter import GetData,Plot1D
import re

parser = OptionParser()
parser.add_option("-d","--dir",help="Specify directory per option for comparison",action="append",default=None)
options,args = parser.parse_args()

if options.dir == None or len(options.dir) == 1:
    print "Please specify at least 2 directories for comparison (separatly using the -d option for each directory)"
    exit()
###################################################################################################################
dataset = { dir:{'data':GetData(dir)} for dir in options.dir }
varlist = []; yearlist = []
for dir,info in dataset.items():
    lumi = info['data']['lumi']
    data = info['data']['limit']
    graphs,mxlist = Plot1D(data)
    info['graph'] = graphs
    if info['data']['variable'] not in varlist: varlist.append(info['data']['variable'])
    if info['data']['year'] not in yearlist: yearlist.append( info['data']['year'] )
################################
c = TCanvas("c","c",800,800)
c.SetLogy()
# c.SetMargin(0.15,0.15,0.15,0.08)
gStyle.SetOptStat(0);
gStyle.SetLegendBorderSize(0);

palette = [color for color in TColor.GetPalette()]

maxX = float('-inf')
minX = float('inf')
maxY = float('-inf')
minY = float('inf') 

limits = TMultiGraph()
mxgraphs = {}
for i,dir in enumerate(options.dir):
    graphs = dataset[dir]['graph']
    colorIter = iter(TColor.GetPalette())
    for j,mx in enumerate(mxlist):
        limit = graphs[mx]
        maxX = max( (maxX, max( max( float(mv) for mv in mvlist ) for mx,mvlist in dataset[dir]['data']['limit'].items() ) ) )
        minX = min( (minX, min( min( float(mv) for mv in mvlist ) for mx,mvlist in dataset[dir]['data']['limit'].items() ) ) )
        maxY = max( (maxY, max( max( lim['exp0'] for mv,lim in mvlist.items() ) for mx,mvlist in dataset[dir]['data']['limit'].items() ) ) )
        minY = min( (minY, min( min( lim['exp0'] for mv,lim in mvlist.items() ) for mx,mvlist in dataset[dir]['data']['limit'].items() ) ) )
        
        if mx not in mxgraphs: mxgraphs[mx] = []
        limit.SetLineStyle(i+1)
        limit.SetLineWidth(3)
        index = int(j*254./(len(mxlist)-1))
        color = palette[ index ]
        limit.SetLineColor( color )
        limits.Add(limit,'l')
####################################################
legend = TLegend(0.2,0.65,0.65,0.82,"")
legend.SetTextSize(0.02)
legend.SetFillColor(0)
# legend.SetNColumns(len(options.dir))
limits.Draw('a l')

for mx in mxlist:
    for dir in options.dir:
        label = 'm_{#chi} = '+mx+' GeV'
        if len(yearlist) >1: label += ' '+dataset[dir]['data']['year']
        if len(varlist) > 1: label += ' '+dataset[dir]['data']['variable']
        legend.AddEntry(dataset[dir]['graph'][mx],label,"l")
##########################################################
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
texS1 = TLatex(0.12092,0.907173,"#bf{CMS} : #it{Preliminary}"+( " ("+yearlist[0]+")" if len(yearlist) == 1 else "" ) );
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
out = ""
if len(yearlist) == 1:
    if len(varlist) == 1: out += yearlist[0]+'_'+varlist[0]
    else:
        out += yearlist[0]
        for var in varlist: out += '_'+var
else:
    if len(varlist) == 1:
        for year in yearlist: out += year + '_'
        out += varlist[0]
    else:
        for i in range(len(varlist)):
            out += yearlist[i]+'_'+varlist[i]
            if i != len(varlist)-1: out += '_'
###########################################################
c.SaveAs("expectedevents1D_"+out+".png")
