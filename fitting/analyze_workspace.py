from ROOT import *

def loop_iterator(iterator):
  object = iterator.Next()
  while object:
    yield object
    object = iterator.Next()

def iter_collection(rooAbsCollection):
  iterator = rooAbsCollection.createIterator()
  return loop_iterator(iterator)

def ListPDF(ws):
    wspdfs = ws.allPdfs()
    return [ pdf.GetName() for pdf in iter_collection(wspdfs) ]
def ListData(ws):
    return [ data.GetName() for data in ws.allData() ]
def ListVars(ws):
    wsvars = ws.allVars()
    return [ var.GetName() for var in iter_collection(wsvars) ]
