import CombineHarvester.CombineTools.ch as ch
from ROOT import TFile,gDirectory
import re
import os
import subprocess

def GetMasses(sysfile):
    rfile = TFile.Open(sysfile)
    rfile.cd('sr')
    regexp = re.compile(r'Mx\d+_Mv\d+$')
    return [ sample.GetName() for sample in gDirectory.GetListOfKeys()
             if regexp.search(sample.GetName()) ]
######################################

def AddSyst(cb,all_proc):
    cb.cp().process(all_proc).AddSyst(
        cb,'lumi','lnN',ch.SystMap()
        (1.026))
    cb.cp().process(all_proc).AddSyst(
        cb,'et_trigg','lnN',ch.SystMap()
        (1.01))
    cb.cp().process(all_proc).AddSyst(
        cb,'bjet_veto','lnN',ch.SystMap()
        (1.02))
    cb.cp().process(['ZJets']).AddSyst(
        cb,'EWK_ZJets','lnN',ch.SystMap()
        (1.10))
    cb.cp().process(['WJets']).AddSyst(
        cb,'EWK_WJets','lnN',ch.SystMap()
        (1.15))
    cb.cp().process(all_proc).AddSyst(
        cb,'jes','shape',ch.SystMap()
        (1.))
    cb.cp().process(all_proc).AddSyst(
        cb,'ewk','shape',ch.SystMap()
        (1.))
    cb.cp().process(all_proc).AddSyst(
        cb,'tracker','shape',ch.SystMap()
        (1.))
    cb.cp().process(all_proc).AddSyst(
        cb,'ecal','shape',ch.SystMap()
        (1.))
    cb.cp().process(all_proc).AddSyst(
        cb,'hcal','shape',ch.SystMap()
        (1.))
######################################

def comhar(sysfile,masses):
    cb = ch.CombineHarvester()
    sr = [ (0,'sr') ]
    cr = [ (1,'e'),(2,'ee'),(3,'m'),(4,'mm') ]
    analysis = ['zprime']
    dataset = ['13TeV']
    channel = ['*']
    cb.AddObservations( ['*'],analysis,dataset,channel,sr+cr )
    
    bkg = ['ZJets','WJets','DiBoson','GJets','TTJets','DYJets','QCD']
    signal = ['$MASS']
    all_proc = signal + bkg
    
    cb.AddProcesses(['*'],analysis,['*'],['*'],bkg,sr+cr,False)
    cb.AddProcesses(masses,analysis,dataset,channel,signal,sr,True)
    AddSyst(cb,all_proc)
    
    cb.cp().process(all_proc).ExtractShapes(
        sysfile,
        "$BIN/$PROCESS",
        "$BIN/$PROCESS_$SYSTEMATIC")

    ###############################################################
    # Add dumpy signal for easier use
    signal = ['${signal}']
    cb.AddProcesses(['*'],analysis,dataset,channel,signal,sr,True)
    AddSyst(cb,signal)

    cb.ForEachObs(lambda x: x.set_rate(-1))
    cb.ForEachProc(lambda x: x.set_rate(-1))
    
    output = TFile("output.root","RECREATE")
    if not os.path.isdir('cards'): os.mkdir('cards')
    
    for b in cb.bin_set():
        print ">> Writing datacard for bin: %s" % b
        cb.cp().bin([b]).mass(['*']).WriteDatacard(
            'cards/%s.txt' % b,output)
######################################################################

def makeCards(sysfile,masses):
    comhar(sysfile,masses)
    subprocess.call(['cp',sysfile,'output.root'])

if __name__ == "__main__":
    from os import getcwd
    sysfile = '/nfs_scratch/ekoenig4/MonoZprimeJet/Run2/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/ZprimeLimits/Systematics/2016/ChNemPtFrac_2016.sys.root'
    
    makeCards(sysfile,['Mx10_Mv1000','Mx50_Mv1000','Mx100_Mv1000'])
