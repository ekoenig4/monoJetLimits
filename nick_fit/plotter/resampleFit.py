#!/usr/bin/env python
import ROOT
import array
import sys
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

def rooIter(coll):
    # PyROOT hasn't iterator-ized the RooFit collections
    if not coll.InheritsFrom(ROOT.RooAbsCollection.Class()):
        raise Exception("Object is not iterable: %r" % coll)
    i = coll.iterator()
    obj = i.Next()
    while obj:
        yield obj
        obj = i.Next()


def makeArgList(coll):
    l = ROOT.RooArgList()
    for item in coll:
        l.add(item)
    return l


# because RooAbsCollection uses operator= for assignment :(
def rooAssign(target, other):
    if target == other:
        return
    for el in rooIter(target):
        theirs = other.find(el)
        if not theirs:
            continue
        el.setVal(theirs.getVal())
        el.setError(theirs.getError())
        el.setAsymError(theirs.getErrorLo(), theirs.getErrorHi())
        el.setAttribute("Constant", theirs.isConstant())


def resample(w, fit, model, fout, treeName):
    pdf = model.GetPdf()
    params = pdf.getParameters(model.GetObservables())
    rooAssign(params, fit.constPars())
    rooAssign(params, fit.floatParsFinal())

    processNorms = {}
    for fn in rooIter(w.allFunctions()):
        if fn.InheritsFrom(ROOT.ProcessNormalization.Class()):
            processNorms[fn.GetName()] = fn

    fout.cd()
    tout = ROOT.TTree(treeName, "Resampled fit result")

    # RooAbsArgs has a protected member attachToTree(TTree*), shame we can't use it :<
    tbranches = [] # Mainly to prevent garbage collection
    vals = {}
    for name, norm in processNorms.iteritems():
        vals[name] = array.array('f', [0.])
        tbranches.append(tout.Branch(name, vals[name], "%s/f" % name))

    params.assignValueOnly(fit.floatParsFinal())
    for name in processNorms.keys():
        vals[name][0] = processNorms[name].getVal()
    tout.Fill()

    for i in range(10000):
        params.assignValueOnly(fit.randomizePars())
        for name in processNorms.keys():
            vals[name][0] = processNorms[name].getVal()
        tout.Fill()

    tout.Write()


if len(sys.argv) < 2:
    print "Usage: ./resampleFit.py workspace.root mlfit.root"
    exit(0)

wfile = ROOT.TFile.Open(sys.argv[-2])
w = wfile.Get("w")
model_b = w.genobj("ModelConfig_bonly")
model_s = w.genobj("ModelConfig")

fitfile = ROOT.TFile.Open(sys.argv[-1])
fit_b = fitfile.Get("fit_b")
fit_s = fitfile.Get("fit_s")

fout = ROOT.TFile("resample.root", "recreate")
resample(w, fit_b, model_b, fout, "resample_fit_b")
resample(w, fit_s, model_s, fout, "resample_fit_s")
data = w.data("data_obs")
data.Write()
# Example data access:
# data.sumEntries("CMS_channel==CMS_channel::ll_bin400to500")
