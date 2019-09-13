
class Process:
    def __init__(self,name,ID=None,shape=( None,None )):
        self.name = name
        self.ID = ID
        self.rate = -1
        self.shape = shape
        self.nuisance = {}
    def addNuisance(self,name,rate): self.nuisance[name] = rate
    def hasShape(self): return self.shape != (None,None)

import re
def sort_nicely( l ):
    """ Sort the given list in the way that humans expect.
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )
    return l

class Datacard:
    def __init__(self,channel):
        self.channel = channel
        self.data_obs = None
        self.signals = []
        self.bkgs = []
        self.processes = {}
        self.nuisances = {}
        self.transfers = []

        #----Style----#
        self.ndash = 100
    def setObservation(self,shape=( None,None )):
        self.data_obs = Process('data_obs',shape=shape)
    def addSignal(self,proc,shape=( None,None )):
        signal = Process(proc, -len(self.signals),shape=shape)
        self.signals.append(proc)
        self.processes[proc] = signal
    def addBkg(self,proc,shape=( None,None )):
        bkg = Process(proc, len(self.bkgs)+1,shape=shape)
        self.bkgs.append(proc)
        self.processes[proc] = bkg
    def addNuisance(self,proc,nuis,ntype,rate):
        if nuis not in self.nuisances: self.nuisances[nuis] = ntype
        self.processes[proc].addNuisance(nuis,rate)
    def addTransfer(self,transfer):
        self.transfers.append(transfer)

    def write(self,fname=None):
        if fname == None: fname = 'datacard_%s' % self.channel
        with open(fname,'w') as card:
            #----Header----#
            card.write('imax * number of bins\n')
            card.write('jmax * number of processes minus 1\n')
            card.write('kmax * number of nuisance parameters\n')
            card.write('-'*self.ndash+'\n')

            #----Shape----#
            def writeShape(process):
                line = 'shapes '
                line += "{0:<15}".format(process.name)
                line += "{0:<5}" .format(self.channel)
                line += "{0:<15}".format(process.shape[0])
                line += "{0:<15}".format(process.shape[1])
                line += process.shape[1]+'_$SYSTEMATIC'
                return line + '\n'
            if self.data_obs.hasShape():
                card.write( writeShape(self.data_obs) )
            for proc in self.signals + self.bkgs:
                process = self.processes[proc]
                if process.hasShape():
                    card.write( writeShape(process) )
            card.write('-'*self.ndash+'\n')

            #----Observation----#
            card.write('bin             %s\n' % self.channel)
            card.write('observation     %s\n' % self.data_obs.rate)
            card.write('-'*self.ndash+'\n')

            #----Processes----#
            proclist = self.signals + self.bkgs
            binline = "{0:<30}".format("bin")
            procline = "{0:<30}".format("process")
            indexline = "{0:<30}".format("process")
            rateline = "{0:<30}".format("rate")
            for proc in proclist:
                process = self.processes[proc]
                binline += "{0:<20}".format(self.channel)
                procline += "{0:<20}".format(process.name)
                indexline += "{0:<20}".format(process.ID)
                rateline += "{0:<20}".format(process.rate)
            for line in (binline,procline,indexline,rateline):
                card.write(line+'\n')
            card.write('-'*self.ndash+'\n')

            #----Nuisance----#
            for nuis in sort_nicely(self.nuisances.keys()):
                line = "{0:<20}".format(nuis)
                line += "{0:<10}".format(self.nuisances[nuis])
                for proc in proclist:
                    process = self.processes[proc]
                    if nuis in process.nuisance:line += "{0:<20}".format(process.nuisance[nuis])
                    else:                       line += "{0:<20}".format('-')
                card.write(line+'\n')
            card.write('-'*self.ndash+'\n')

            #----Transfer----#
            for transfer in sort_nicely(self.transfers):
                card.write( '{0:<20}'.format(transfer)+' param 0 1\n')
#################################################################################################
            


            
            
            
            
