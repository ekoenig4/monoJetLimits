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
        sysdir = next( sub for sub in inputdir.split('/') if '.sys' in sub )
        if year is not 'Run2': wsfiles = [TFile.Open('../workspace_%s.root' % year)]
        else: wsfiles = [ TFile.Open('../workspace_%s.root' % y) for y in ('2016','2017','2018') ]
        self.lumi = sum( wsfile.Get('lumi').Integral() for wsfile in wsfiles )
        self.lumi_label = self.lumi_label = '%s' % float('%.3g' % (self.lumi/1000.)) + " fb^{-1}"
        self.year = str(int(float(wsfiles[0].Get('year').Integral()))) if year is not 'Run2' else 'Run2'
        self.variable = wsfiles[0].Get('variable').GetTitle()
        self.cut = sysdir.split("_")[0].replace(self.variable,'')
        self.mods = sysdir.split("_")[-1].replace('.sys','')
        self.sysdir = sysdir.replace('.sys','').replace('_%s' % self.year,'')
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
