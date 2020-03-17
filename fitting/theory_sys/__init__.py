from ROOT import TFile
import os

filedir = os.path.dirname( os.path.realpath(__file__) )

theoryfnames = {
    "wsr_to_zsr":"wz_unc.root",
    "ga_to_sr":"gz_unc.root"
}

theoryfiles = { key:TFile("%s/%s"%(filedir,fname)) for key,fname in theoryfnames.iteritems() }
theoryhistos = { key:{ hkey.GetName():tfile.Get(hkey.GetName()) for hkey in tfile.GetListOfKeys() } for key,tfile in theoryfiles.iteritems() }

nuisancemap = {
    "QCD_Scale":"QCDScale",
    "QCD_Proc":"QCDProcess",
    "QCD_Shape":"QCDShape",
    "NNLO_EWK":"NNLOEWK",
    "NNLO_Sud":"Sudakov",
    "NNLO_Miss":"NNLOMiss",
    "QCD_EWK_Mix":"MIX",
    "PDF":"PDF"
}

uncorrelatedmap = {
    "zsr":"1",
    "wsr":"2",
    "sr":"1",
    "ga":"2"
}

def getTFShift(tfname,nuisance,histomap=theoryhistos,ch='monojet'):
    if ch is 'monojet': ch = lambda string:"monov" not in string
    else: ch = lambda string:"monov" in string
    # print tfname,nuisance
    histomap = histomap[tfname]
    nuistype,hstype = next( nuistype for nuistype in nuisancemap.iteritems() if nuistype[0] in nuisance )
    if any(nuisance.replace(nuistype,"")): hstype += uncorrelatedmap[ nuisance.replace(nuistype+"_","") ]
    hskey,shiftUp = next( (key,hs) for key,hs in histomap.iteritems() if hstype in key and ch(key) and 'Down' not in key)
    shiftDn = histomap[hskey+'_Down']
    return shiftUp,shiftDn
if __name__ == "__main__":
    print getTFShift("wsr_to_zsr","NNLO_Sud_zsr")
    print getTFShift("wsr_to_zsr","NNLO_Sud_wsr")
    print getTFShift("ga_to_sr","QCD_EWK_Mix")
