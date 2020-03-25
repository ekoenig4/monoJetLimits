from ROOT import *
import os
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f","--files",help="Files to merge into one sys file",nargs="+",type=TFile,required=True)
parser.add_argument("-c","--categories",help="Catergory name to give to each sys file in merged file",nargs="+",required=True)
parser.add_argument("-o","--output",help="Output filename",type=lambda fn:TFile(fn,"recreate"),required=True)

args = parser.parse_args()
for tfile,cat in zip(args.files,args.categories):
    args.output.cd()
    tdir = args.output.mkdir(cat)
    tdir.cd()
    for key in tfile.GetListOfKeys(): tfile.Get(key.GetName()).Write()
    tdir.Write()
args.output.Close()

