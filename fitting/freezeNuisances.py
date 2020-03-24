from ROOT import *
from argparse import ArgumentParser
import os
import re

def getargs():
    parser = ArgumentParser()
    parser.add_argument("-w","--workspace",required=True)

    def compile_pattern(pattern,prompt):
        print prompt,pattern
        return re.compile(pattern)
    
    parser.add_argument("-i","--ignore",nargs="+",default=[re.compile("met_monojet_.*"),re.compile("recoil"),re.compile("r")],type=lambda arg:compile_pattern(arg,"Compile Ignore:"))
    parser.add_argument("-f","--freeze",nargs="+",default=[re.compile(".*")],type=lambda arg:compile_pattern(arg,"Compile Freeze:"))
    parser.add_argument("-t","--thaw",nargs="+",default=[],type=lambda arg:compile_pattern(arg,"Compile Thaw:"))
    parser.add_argument("-d","--display",action="store_true",default=False)
    parser.add_argument("-o","--output")
    return parser.parse_args()
def setiter(rooset):
    iter = rooset.createIterator()
    obj = iter.Next()
    while obj:
        yield obj
        obj = iter.Next()
def FreezeNuisances():
    args = getargs()
    tfile = TFile(args.workspace)
    ws = tfile.Get("w")
        
    variables = [ var for var in setiter(ws.allVars())
                  if not var.isConstant() and
                  any( pattern.match(var.GetName()) for pattern in args.freeze ) and
                  not any( pattern.match(var.GetName()) for pattern in args.thaw) and
                  not any( pattern.match(var.GetName()) for pattern in args.ignore )]
    variables.sort(key=lambda var:var.GetName())
    
    for var in variables:
        var.Print()
        if args.display: continue
        var.setConstant(1)
    if args.display: return
    if args.output == None: args.output = "frozen_"+tfile.GetName()
    print "Writing Frozen Workspace to",args.output
    output = TFile(args.output,"recreate")
    ws.Write()
    output.Write()
    
    
if __name__ == "__main__": FreezeNuisances()
