import os
import json
import re
from ROOT import TFile
from SysInfo import SysInfo

class Limits(SysInfo):
    def __init__(self,inputdir):
        home = os.getcwd()
        SysInfo.__init__(self,inputdir)
        os.chdir(inputdir)
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
            #print("hi")
            #print(mvinfo.keys())
            #print(type(mvinfo.keys()[0]))
            #print(mvinfo.keys()[0])
            #print("bye")
        if exclude is not None: exclude(datalist)
        return datalist
    def __str__(self): return SysInfo.__str__(self)
#####################################################################
