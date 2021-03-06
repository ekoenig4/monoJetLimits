import os
import re
from ROOT import TFile

class SysInfo:
    def __init__(self,inputdir):
        home = os.getcwd()
        os.chdir(inputdir)
        self.cwd = os.getcwd()
        year = re.findall('\d\d\d\d',inputdir)
        if not any(year): year = 'Run2'
        else: year = year[0]
        path = inputdir.split('/')
        sysdir = next( sub for sub in path if '.sys' in sub )
        label = next( path[i] for i in range(len(path)) if sysdir == path[i+1] )
        if year is not 'Run2': wsfiles = [TFile.Open('../workspace_%s.root' % year)]
        else: wsfiles = [ TFile.Open('../%s'%fname) for fname in os.listdir("../") if "workspace" in fname ]
        self.lumi = sum( wsfile.Get('lumi').Integral() for wsfile in wsfiles )
        self.lumi_label = self.lumi_label = '%s' % float('%.3g' % (self.lumi/1000.)) + " fb^{-1}"
        self.year = str(int(float(wsfiles[0].Get('year').Integral()))) if year is not 'Run2' else 'Run2'
        self.variable = wsfiles[0].Get('variable').GetTitle()
        self.cut = sysdir.split("_")[0].replace(self.variable,'')
        self.mods = sysdir.split("_")[-1].replace('.sys','')
        self.sysdir = sysdir.replace('.sys','').replace('_%s' % self.year,'')
        self.label = label
        os.chdir(home)
    def __str__(self):
        string  = 'Directory: %s\n' % self.cwd
        string += 'SysDir:    %s\n' % self.sysdir
        string += 'Year:      %s\n' % self.year
        string += 'Lumi:      %f\n' % self.lumi
        string += 'variable:  %s\n' % self.variable
        string += 'cut:       %s\n' % self.cut
        string += 'mods:      %s\n' % self.mods
        return string
    def getOutputDir(self,outdir_base):
        outdir = outdir_base % self.year
        output = '%s/%s/%s/' % (outdir,self.variable,self.label)
        return output
