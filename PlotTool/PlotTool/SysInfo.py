import os
import re
from ROOT import TFile

class SysInfo:
    def __init__(self,inputdir):
        home = os.getcwd()
        os.chdir(inputdir)
        self.cwd = os.getcwd()
        sysdir = next( sub for sub in inputdir.split('/') if '.sys' in sub )
        wsfile = TFile.Open('../workspace.root')
        self.lumi = wsfile.Get('lumi').Integral()
        self.year = str(int(float(wsfile.Get('year').Integral())))
        self.variable = wsfile.Get('variable').GetTitle()
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
