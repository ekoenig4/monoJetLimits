from Dataset import Dataset


class SelectorResult:
    def __init__(self, inputFile, luminosity=1000, crossSectionOverrides=None):
        self._file = inputFile

        self._datasets = {}
        for key in self._file.GetListOfKeys():
            if key.GetClassName() == "TDirectoryFile":
                d = Dataset(key.ReadObj(), luminosity)
                if d.isValid():
                    self._datasets[key.GetName()] = d

        dsPlots = (set(d.plots()) for d in self._datasets.values())
        self._plots = reduce(lambda a, b: a & b, dsPlots)

        if type(crossSectionOverrides) is dict:
            for ds, newValue in crossSectionOverrides.iteritems():
                self._datasets[ds].setCrossSection(newValue)
        elif not crossSectionOverrides:
            pass
        else:
            raise Exception("crossSectionOverrides needs to be a dict, (dataset_name, value_in_pb)")

    def __repr__(self):
        return '<SelectorResult instance ("%s", %d datasets, %d plots)>' % (self._file.GetName(), len(self._datasets), len(self._plots))

    def plots(self):
        return self._plots

    def datasets(self):
        return set(self._datasets.keys())

    def hasDataset(self, datasetName):
        return datasetName in self._datasets

    def getDataset(self, datasetName):
        if datasetName not in self._datasets:
            raise Exception("No dataset named %s in %s" % (datasetName, repr(self)))
        return self._datasets[datasetName]
