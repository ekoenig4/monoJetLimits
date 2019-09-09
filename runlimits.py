import os
import sys
from optparse import OptionParser
import threading
from combineDir import combine,combineTool
from makeCards import GetMasses

def combineCard(regions):
    arg = 'combineCards.py '
    for region in regions: arg += '%s=cards/%s.txt ' % (region,region)
    arg += ' > cards/zprime_card.txt'
    os.system(arg)
##############################################################################
parser = OptionParser()
parser.add_option("-d","--dir",help='Specify the directory to run limits in',action='store',type='str',default=None)
parser.add_option("--cr",help='Uses CR in fit',action='store_true',default=False)
options,args = parser.parse_args()
if options.dir == None:
    print "Please specify a director to run limits in."
    exit()
##########
os.chdir(options.dir)
masses = GetMasses('output.root')
if not options.cr: regions = ('sr',)
else:              regions = ('sr','e','ee','m','mm')
print 'Generating Cards...'
combineCard(regions)
print 'Done'
cwd = os.getcwd()
class thread (threading.Thread):
    def __init__(self,signals):
        threading.Thread.__init__(self)
        self.signals = signals
        self.nfile = 0
    def run(self): self.runlimit(self.signals)
    def runlimit(self,signals):
        for signal in signals: combine(signal)
#############################################################################

threads = {}
n = 3 # number of signal per thread
signal_split = [masses[i * n:(i + 1) * n] for i in range((len(masses) + n - 1) // n )]
for signals in signal_split:
    threads[str(signals)] = thread(signals)
    threads[str(signals)].start()
print '%i Threads Started' % len(threads)
while any(threads):
    change = False
    idlist = threads.keys()
    for id in idlist:
        if not threads[id].isAlive():
            threads.pop(id)
            change = True
    if change:
        out = '\r%i Threads Remaining' % len(threads)
        sys.stdout.write(out)
        sys.stdout.flush()
print
print 'Combined Finished.'
#################################################################################################
