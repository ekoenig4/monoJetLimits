from ROOT import *
import os
from shutil import copy2 as copy
from optparse import OptionParser
from array import array
from makeShapeCards import MakeShapeCard

parser = OptionParser()
parser.add_option("-i","--input",help="Specify input systematics file to generate limits from",action="store",type="str",default=None)

options,args = parser.parse_args()

if 'Systematics/' in options.input:
    f = options.input.split('/')[1:]
    label = ""
    for l in f[:-1]: label += '_'+l
    fname = f[-1].replace('.root',label+'.root')
else: fname = options.input.split('/')[-1]
rfile = TFile.Open(options.input)
rfile.cd('sr')
keylist = [ key.GetName() for key in gDirectory.GetListOfKeys() ]
signals = [ key for key in keylist if 'Mx' in key and 'Mv' in key and 'Up' not in key and 'Down' not in key ]
signalList = {}
for i,signal in enumerate(signals):
    mx = signal.replace('Mx','').split('_')[0]
    mv = signal.replace('Mv','').split('_')[1]
    if mx not in signalList: signalList[mx] = []
    signalList[mx].append(mv)
    signalList[mx].sort(key=int)
##########################################################
dir = 'Limits/'+fname.replace('.root','')
if not os.path.isdir(dir): os.mkdir(dir)
copy(options.input,dir+'/'+fname)
for mx in sorted(signalList.keys()):
    print 'Mx: '+mx
    for mv in signalList[mx]:
        print '\tMv: '+mv
        MakeShapeCard(mx,mv,fname,dir)

