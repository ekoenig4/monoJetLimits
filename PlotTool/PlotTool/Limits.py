import os
import json
import re
from ROOT import TFile

class Limits:
    def __init__(self,inputdir):
        home = os.getcwd()
        os.chdir(inputdir)
        self.cwd = os.getcwd()
        self.sysdir = next( sub for sub in inputdir.split('/') if '.sys' in sub )
        wsfile = TFile.Open('workspace.root')
        self.lumi = wsfile.Get('lumi').Integral()
        self.year = str(int(float(wsfile.Get('year').Integral())))
        self.variable = wsfile.Get('variable').GetTitle()
        info = self.sysdir.replace('.sys','').replace(self.variable,'').replace(self.year,"").split('_')
        self.cut = info[0]
        self.extra = re.findall('...',info[1])
        with open('limits.json') as f: d_json = json.load(f)
        self.data = {}
        for mx,mxinfo in d_json.iteritems():
            mxlim = {}
            for mv,mvinfo in mxinfo.iteritems():
                scale = d_json[mx][mv]['scale']
                mxlim[mv] = { exp:scale*val for exp,val in mvinfo['limits'].iteritems() }
            self.data[mx] = mxlim
        os.chdir(home)
    def getDatalist(self,exclude=None):
        datalist = {}
        for mx,mvinfo in self.data.iteritems():
            datalist[mx] = mvinfo.keys()
        if exclude is not None: exclude(datalist)
        return datalist
#####################################################################
