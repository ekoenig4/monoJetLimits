#!/usr/bin/env python
from ROOT import *
import os
from argparse import ArgumentParser
import json
from array import array
from PlotTool import *

gROOT.SetBatch(1)

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoJet/Plots%s/ExpectedLimits/"
mxval = u'1'
def one_mx(data):
    include_central(data)
    mxlist = data.keys()
    for mx in mxlist:
        if mx != mxval: data.pop(mx)

def GetLabel(data):
    info = data['info']
    label = '%s m_{#chi} = %s' % (info.year,mxval)
    if 'nCR' in info.mods: label = '%s no CR' % label
    else:                  label = '%s Sim Fit' % label
    if 'nSYS' in info.mods: label = '%s no Systematics' % label
    else:                   label = '%s with Systematics' % label
    if 'nPFU' in info.mods: label = '%s no PFU' % label
    if 'nJES' in info.mods: label = '%s no JES' % label
    return label

def compareLimits(norm,inputs):
    limitmap = { directory:{'info':Limits(directory)} for directory in [norm] + inputs }
    for directory,data in limitmap.iteritems(): data['graph'],data['mxlist'] = Plot1D(data['info'],one_mx);
    
    c = TCanvas("c","c",800,800)
    c.SetLogy()
    # c.SetMargin(0.15,0.15,0.15,0.08)
    gStyle.SetOptStat(0);
    gStyle.SetLegendBorderSize(0);
    
    pad1 = TPad("pad1","pad1",0.01,0.25,0.99,0.99);
    pad1.Draw(); pad1.cd();
    pad1.SetLogy();
    pad1.SetFillColor(0); pad1.SetFrameBorderMode(0); pad1.SetBorderMode(0);
    pad1.SetBottomMargin(0.);

    norm_g = limitmap[norm]['graph'][mxval]
    var_gs = { input:limitmap[input]['graph'][mxval] for input in inputs }
    coliter = iter(colormap.values())
    var_col = { input:next(coliter) for input in inputs }

    norm_g.Draw('ap'); data_style(norm_g)
    norm_g.GetYaxis().SetRangeUser(10**-3.5,10**5.5)
    norm_g.GetYaxis().SetTitle("95% CL limit on #sigma/#sigma_{theory}")
    for name,var_g in var_gs.iteritems():
        var_g.Draw('l same'); fit_style(var_g,var_col[name]); var_g.SetLineWidth(3)
    norm_g.Draw('p same')

    leg = getLegend(xmin=0.5,xmax=0.7)
    leg.AddEntry(norm_g,GetLabel(limitmap[norm]),'p')
    for name,var_g in var_gs.iteritems():
        leg.AddEntry(var_g,GetLabel(limitmap[name]),'l')
    leg.Draw()
    #################################################
    c.cd()
    pad2 = TPad("pad2","pad2",0.01,0.01,0.99,0.25);
    pad2.Draw(); pad2.cd();
    pad2.SetTopMargin(0);
    pad2.SetFillColor(0); pad2.SetFrameBorderMode(0);
    pad2.SetBorderMode(0);
    pad2.SetBottomMargin(0.35);

    ratios = { input:GetRatio(norm_g,var_g) for input,var_g in var_gs.iteritems() }
    first = True
    for name,ratio in ratios.iteritems():
        if first: ratio.Draw('al'); first = False
        else:     ratio.Draw('l')
        ratio_style(ratio,var_col[name],name='Norm/Var')
        ratio.SetLineWidth(2)
        ratio.SetLineColor(var_col[name])
        ratio.GetXaxis().SetTitle("m_{med} (GeV)")
        ratio.GetYaxis().SetTitleSize(0.1)
        ratio.GetYaxis().SetTitleOffset(0.5)
        ratio.GetYaxis().SetLabelSize(0.1)

    norm_info = limitmap[norm]['info']
    input_info = {input:limitmap[input]['info'] for input in inputs }
    outdir = outdir_base % norm_info.year; checkdir(outdir)
    outdir += '/%s' % norm_info.variable; checkdir(outdir)
    outdir += '/%s' % norm_info.sysdir; checkdir(outdir)
    outdir += '/ratios'; checkdir(outdir)
    input_label ='_'.join([input_info[input].sysdir for input in inputs])
    fname = 'ratio_%s_vs_%s.png' % (norm_info.sysdir,input_label)
    c.SaveAs('%s/%s' % (outdir,fname))
    
def getargs():
    parser = ArgumentParser()
    parser.add_argument('-n','--numerator',help='Specify the norm limits to compare everything to',action='store',required=True)
    parser.add_argument('-d','--denomenator',help='Specify input limits to comapre to the norm limit',nargs='+',action='store',required=True)
    args = parser.parse_args()
    if args.numerator in args.denomenator: args.denomenator.remove(args.numerator)
    return args

if __name__ == "__main__":
    args = getargs()
    compareLimits(args.numerator,args.denomenator)


