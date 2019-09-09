import os
import sys
import re

#############################################################################
def combine(signal,show=False):
    mx = signal.split('_')[0].replace('Mx','')
    mv = signal.split('_')[1].replace('Mv','')
    os.system("export signal='%s'" % signal)
    os.system("envsubst \$signal < .cards/zprime_card.txt > .cards/%s.txt" % signal)
    arg = 'combine -M AsymptoticLimits -n Mx%sMv%sGeV -m %s .cards/%s.txt' % (mx,mv,mv,signal)
    if not show: arg += ' >/dev/null'
    os.system(arg)
    if not os.path.isdir('Mx%s'%mx): os.mkdir('Mx%s'%mx)
    os.system('mv higgsCombineMx%sMv%sGeV.AsymptoticLimits.mH%s.root Mx%s/' % (mx,mv,mv,mx))
    os.system('rm .cards/%s.txt' % signal)
#############################################################################
def combineTool(dir,output,show=False):
    arg = 'combineTool.py -M CollectLimits '+dir+'/higgsCombine*.root -o '+output
    if not show: arg += ' >/dev/null'
    os.system(arg)
##############################################################################

if __name__ == "__main__":
    combine("Mx10_Mv1000",show=True)
