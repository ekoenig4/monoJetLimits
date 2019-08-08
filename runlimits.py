import os
import sys
from optparse import OptionParser
import threading
from combineDir import combine,combineTool
    
parser = OptionParser()
parser.add_option("-d","--dir",help='Specify the directory to run limits in',action='store',type='str',default=None)
options,args = parser.parse_args()
if options.dir == None:
    print "Please specify a director to run limits in."
    exit()
##########
os.chdir(options.dir)
mxdir = [ dir for dir in os.listdir('.') if os.path.isdir(dir) ]
mxdir.sort( key=lambda d:int(d.split('_')[-1]) )
cwd = os.getcwd()

class thread (threading.Thread):
    def __init__(self,dir):
        threading.Thread.__init__(self)
        self.dir = dir
        self.nfile = 0
    def run(self): self.runlimit(dir)
    def runlimit(self,dir):
        mvfiles = [ dir+'/'+file for file in os.listdir(dir) if 'zprimeMx' in file and '_shape.txt' in file ]
        mvfiles.sort( key=lambda f: int( f.split('_')[2].replace('Mv','') ) )
        self.nfile = len(mvfiles)
        for mvfile in mvfiles: combine(dir,mvfile); self.nfile -= 1
        combineTool(dir,dir+'/limits_shape_'+dir+'.json')
#############################################################################

threads = {}
for dir in mxdir:
    threads[dir] = thread(dir)
    threads[dir].start()

last = ""
while any(threads):
    out = "\r"+str(len(threads))+" Thread(s) Remaining"
    mxdir = sorted( threads.keys(),key=lambda d: int( d.split('_')[1] ) )
    for dir in mxdir:
        if not threads[dir].isAlive(): threads.pop(dir)
        else:
            out += "\n\r"+dir+":"+str(threads[dir].nfile)
    if out != last:
        last = out
        sys.stdout.write(out)
        sys.stdout.flush()
print
#################################################################################################
