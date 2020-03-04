import os
import sys
import re

#############################################################################
def combine(signal,show=False):
    mx = signal.split('_')[0].replace('Mchi','')
    mv = signal.split('_')[1].replace('Mphi','')
    os.system("export signal='%s'" % signal)
    os.system("envsubst \$signal < .cards/zprime_card.txt > .cards/%s.txt" % signal)
    arg = 'combine -M AsymptoticLimits -n Mchi%sMphi%sGeV -m %s .cards/%s.txt' % (mx,mv,mv,signal)
    if not show: arg += ' >/dev/null'
    os.system(arg)
    if not os.path.isdir('Mchi%s'%mx): os.mkdir('Mchi%s'%mx)
    os.system('mv higgsCombineMchi%sMphi%sGeV.AsymptoticLimits.mH%s.root Mchi%s/' % (mx,mv,mv,mx))
    os.system('rm .cards/%s.txt' % signal)
#############################################################################
def combineTool(dir,output,show=False):
    arg = 'combineTool.py -M CollectLimits '+dir+'/higgsCombine*.root -o '+output
    if not show: arg += ' >/dev/null'
    os.system(arg)
##############################################################################

if __name__ == "__main__":
    combine("Mchi10_Mphi1000",show=True)
