import os
import sys
import re

def combine(dir,fname,show=False):
    mx = dir.split('_')[1]
    mv = fname.split('_')[2].replace('Mv','')
    arg = 'combine -M AsymptoticLimits -n Mx'+mx+'Mv'+mv+'GeV -m '+mv+' '+fname
    if not show: arg += ' >/dev/null'
    os.system(arg)
    os.system('mv higgsCombineMx'+mx+'Mv'+mv+'GeV.AsymptoticLimits.mH'+mv+'.root '+dir+'/')
#############################################################################
def combineTool(dir,output,show=False):
    arg = 'combineTool.py -M CollectLimits '+dir+'/higgsCombine*.root -o '+output
    if not show: arg += ' >/dev/null'
    os.system(arg)
##############################################################################

if __name__ == "__main__":
    dir = sys.argv[-1]
    subdir = re.search(r'Mx_\d*/',dir).group(0).replace('/','')
    dir = dir.replace(subdir,'')
    os.chdir(dir)
    dir = subdir
    mvfiles = [ dir+'/'+file for file in os.listdir(dir) if 'zprimeMx' in file and '_shape.txt' in file ]
    mvfiles.sort( key=lambda f: int( f.split('_')[2].replace('Mv','') ) )
    for mvfile in mvfiles: combine(dir,mvfile,show=True);
    combineTool(dir,dir+'/limits_shape_'+dir+'.json',show=True)
