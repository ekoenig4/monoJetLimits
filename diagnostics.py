#!/usr/bin/env python
import os,re
from argparse import ArgumentParser
from subprocess import Popen,STDOUT,PIPE
from shutil import copyfile
from ROOT import *

outdir_base = "/afs/hep.wisc.edu/home/ekoenig4/public_html/MonoZprimeJet/Plots%s/ExpectedLimits/"
def mvdiagnostics(sysdir):
    first = sysdir.split('_')[0]
    second = sysdir.split('_')[1]
    variable = re.findall('^.*[\+-]',first)
    if not any(variable): variable = first
    else: variable = variable[0][:-1]
    year = re.findall('\d\d\d\d',second)[0]
    outdir = outdir_base % year
    outname = 'fit_%s' % sysdir.replace('.sys','')
    outdir = '%s/%s/' % (outdir,outname)
    if not os.path.isdir(outdir): os.mkdir(outdir)
    for png in os.listdir('diagnostics'):
        if '.png' in png:
            print 'Moving diagonstics/%s to %s/%s' % (png,outdir,png)
            copyfile( 'diagnostics/%s' % png,'%s/%s' % (outdir,png) )
def PlotDiagnostics():
    gROOT.SetBatch(1)
    tfile = TFile.Open('fitDiagnostics.root')
    def plotFit(dir):
        outname = dir.GetName()
        mclist = ('ZJets','WJets','DiBoson','GJets','TTJets','DYJets','QCD')
        dir = dir.GetDirectory('sr')
        c= TCanvas('c','c',800,800)
        gStyle.SetOptStat(0);
        gStyle.SetLegendBorderSize(0);
        c.SetLeftMargin(0.15);
        c.SetLogy();
        c.cd();
        
        bkg = dir.Get('total_background').Clone('SumOfBkg')
        data = dir.Get('data')           .Clone('data_obs')
        signal = dir.Get('total_signal') .Clone('Signal')

        minY = min( array.GetMinimum() for array in (bkg,signal) )
        maxY = max( array.GetMaximum() for array in (bkg,signal) )

        bkg.SetMinimum(0.1)
        bkg.SetMaximum(100*maxY)
        bkg.SetFillColor(kGray)
        bkg.SetLineColor(kBlack)
        bkg.SetTitle("")
        bkg.Draw('hist same')

        data.SetMarkerStyle(20)
        data.SetMarkerSize(0.9)
        data.Draw('pex0 same')

        signal.SetLineColor(kBlue)
        signal.SetLineWidth(2)
        signal.Draw('hist same')

        leg = TLegend(0.62,0.60,0.86,0.887173,'')
        leg.SetFillColor(kWhite); leg.SetFillStyle(0)
        leg.SetTextSize(0.025)
        leg.AddEntry(data,data.GetName(),'lp')
        leg.AddEntry(signal,signal.GetName(),'l')
        leg.AddEntry(bkg,bkg.GetName(),'f')
        leg.Draw()
        
        c.SaveAs('%s.png' % outname)
    
    for fit in ('prefit','fit_b','fit_s'):
        fdir = tfile.GetDirectory('shapes_%s' % fit)
        plotFit(fdir)
def RunDiagnostics():
    def run(command):
        print ' '.join(command)
        proc = Popen(command)
        proc.wait()
    blind = ['-t','-1','--expectSignal','1']
    diagnostics = ['combine','-M','FitDiagnostics','--saveShapes','--saveOverallShapes','--saveNormalizations','--saveWithUncertainties']
    card = ['-d','datacard']
    run(diagnostics + card + blind)
def getargs():
    def directory(arg):
        if os.path.isdir(arg): return arg
        print arg,'invalid directory'
        raise ValueError()
    def signal(arg):
        regex = re.compile(r"Mx\d*_Mv\d*$")
        if regex.match(arg): return arg
        print arg,'invalid signal'
        raise ValueError()
    parser = ArgumentParser(description='Run all avaiable limits in specified directory')
    parser.add_argument("-d","--dir",help='Specify the directory to run limits in',action='store',type=directory,required=True)
    parser.add_argument("-s","--signal",help='Specify the signal (Mxd_Mvd) sample to get impact for',action='store',type=signal,required=True)
    try: args = parser.parse_args()
    except ValueError():
        parser.print_help()
        exit()
    return args
##############################################################################
if __name__ == "__main__":
    args = getargs()
    os.chdir(args.dir)
    cwd = os.getcwd()
    sysdir = next( sub for sub in cwd.split('/') if '.sys' in sub )
    mx = args.signal.split('_')[0].replace('Mx','')
    mxdir = 'Mx_%s' % mx
    mv = args.signal.split('_')[1].replace('Mv','')
    dir = 'diagnostics'
    if not os.path.isdir(dir): os.mkdir(dir)
    else:                      os.system('rm diagnostics/*')
    with open('%s/datacard' % mxdir,'r') as f: card = f.read().replace('$MASS',mv)
    with open('%s/datacard' % dir,'w') as f: f.write(card)
    os.chdir(dir)
    RunDiagnostics()
    PlotDiagnostics()
    os.chdir(cwd)
    mvdiagnostics(sysdir)
