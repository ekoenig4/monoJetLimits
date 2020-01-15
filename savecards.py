import os
import sys
from shutil import copyfile

if not os.path.isdir('workspace'): os.mkdir('workspace')
output = os.path.abspath('workspace')
inputdir = sys.argv[1]
os.chdir(inputdir)
[ copyfile('../%s' % ws,'%s/%s' % (output,ws)) for ws in os.listdir('../') if 'workspace' in ws ]
if not os.path.isdir('%s/datacards' % output): os.mkdir('%s/datacards' % output)

def savecard(input,output):
    print input,output
    for item in os.listdir(input):
        if 'datacard' in item or 'workspace' in item: copyfile('%s/%s' % (input,item),'%s/%s' % (output,item))
        if os.path.isdir('%s/%s' % (input,item)) and ('Mx' in item or 'Mv' in item):
            if not os.path.isdir('%s/%s' % (output,item)): os.mkdir('%s/%s' % (output,item))
            savecard('%s/%s' % (input,item),'%s/%s' % (output,item))

savecard('.','%s/datacards' % output)


