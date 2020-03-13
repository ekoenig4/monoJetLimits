
class Process:
    def __init__(self,name,ID=None,shape=( None,None ),rate=-1):
        self.name = name
        self.ID = ID
        self.rate = rate
        self.shape = shape
        self.nuisances = {}
    def addNuisance(self,name,rate): self.nuisances[name] = rate
    def hasShape(self): return self.shape != (None,None)
    def removeNuisance(self,name):
        if name in self.nuisances: self.nuisances.pop(name)

import re
def sort_nicely( l ):
    """ Sort the given list in the way that humans expect.
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )
    return l

class Datacard:
    def __init__(self,channel,ws):
        self.channel = channel
        self.ws = ws
        self.data_obs = None
        self.signals = []
        self.models = []
        self.bkgs = []
        self.processes = {}
        self.nuisances = {}
        self.transfers = []

        #----Style----#
        self.ndash = 100
    def setObservation(self,shape=None):
        self.data_obs = Process('data_obs',shape=(self.ws.fname,shape))
    def addSignal(self,proc,shape=None):
        signal = Process(proc, -len(self.signals),shape=(self.ws.fname,shape))
        self.signals.append(proc)
        self.processes[proc] = signal
    def addModel(self,proc,shape=None,rate=1):
        model = Process(proc,len(self.bkgs)+1,shape=(self.ws.fname,shape),rate=rate)
        self.bkgs.append(proc)
        self.models.append(proc)
        self.processes[proc] = model
    def addBkg(self,proc,shape=None,rate=-1):
        bkg = Process(proc, len(self.bkgs)+1,shape=(self.ws.fname,shape),rate=rate)
        self.bkgs.append(proc)
        self.processes[proc] = bkg
    def addNuisance(self,proc,nuis,ntype,rate):
        if proc not in self.processes: return
        if nuis not in self.nuisances: self.nuisances[nuis] = ntype
        self.processes[proc].addNuisance(nuis,rate)
    def addTransfer(self,transfer):
        self.transfers.append(transfer)

    def removeNuisance(self,proc,nuis):
        if proc not in self.processes: return
        if nuis not in self.nuisances: return
        self.processes[proc].removeNuisance(nuis)
        for name,process in self.processes.iteritems():
            if nuis in process.nuisances: return
        self.nuisances.pop(nuis)

    def write(self,fname=None,wildcard=True,autostat=False):
        if fname == None: fname = 'datacard_%s' % self.channel
        with open(fname,'w') as card:
            #----Header----#
            card.write('imax * number of bins\n')
            card.write('jmax * number of processes minus 1\n')
            card.write('kmax * number of nuisance parameters\n')
            card.write('-'*self.ndash+'\n')

            #----Shape----#
            def writeShape(process="*",channel="*",fname=self.ws.fname,shape="$PROCESS_$CHANNEL",sys=True):
                if type(process) is Process:
                    return writeShape(process.name,self.channel,fname=process.shape[0],shape=process.shape[1],sys=sys)
                line = 'shapes '
                line += "{0:<25}".format(process)
                line += "{0:<10}" .format(channel)
                line += "{0:<25}".format(fname)
                line += "{0:<35}".format("w:"+shape)
                if sys: line += ' w:'+shape+'_$SYSTEMATIC'
                return line + '\n'
            if wildcard:
                for model in self.models:
                    model = self.processes[model]
                    card.write( writeShape(model.name,self.channel,shape=model.shape[1]) )
                for signal in self.signals:
                    signal = self.processes[signal]
                    card.write( writeShape(signal.name,shape=signal.shape[1].replace(self.channel,"$CHANNEL")) )
                card.write(writeShape())
            else:
                if self.data_obs.hasShape():
                    card.write( writeShape(self.data_obs,sys=False) )
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
            binline = "{0:<35}".format("bin")
            procline = "{0:<35}".format("process")
            indexline = "{0:<35}".format("process")
            rateline = "{0:<35}".format("rate")
            for proc in proclist:
                process = self.processes[proc]
                binline += "{0:<30}".format(self.channel)
                procline += "{0:<30}".format(process.name)
                indexline += "{0:<30}".format(process.ID)
                rateline += "{0:<30}".format(process.rate)
            for line in (binline,procline,indexline,rateline):
                card.write(line+'\n')
            card.write('-'*self.ndash+'\n')

            #----Nuisance----#
            for nuis in sort_nicely(self.nuisances.keys()):
                line = "{0:<25}".format(nuis)
                line += "{0:<10}".format(self.nuisances[nuis])
                for proc in proclist:
                    process = self.processes[proc]
                    if nuis in process.nuisances:line += "{0:<30}".format(process.nuisances[nuis])
                    else:                        line += "{0:<30}".format('-')
                card.write(line+'\n')
            card.write('-'*self.ndash+'\n')

            if autostat: card.write("%s autoMCStats 0\n" % self.channel)
            #----Transfer----#
            for transfer in sort_nicely(self.transfers):
                card.write( '{0:<30}'.format(transfer)+' param 0 1\n')
#################################################################################################
            


            
            
            
            
