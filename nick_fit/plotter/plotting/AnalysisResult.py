from plotGroups import allPlotGroups, parseSpecialPlotGroup


class AnalysisResult:
    def __init__(self, args, selectorResults):
        self.selectorResults = selectorResults

        self.stackGroups = []
        for plotGroupName in args.stack.split(','):
            pg = self.setupPlotGroup(plotGroupName)
            pg._type = pg.Stackable
            self.stackGroups.append(pg)

        self.signalGroups = []
        if args.signal:
            for sigName in args.signal:
                pg = self.setupPlotGroup(sigName)
                pg._type = pg.SignalLike
                self.signalGroups.append(pg)

        # Plural since either 0 or 1 datas...right?
        self.dataGroups = []
        # runPlotter has --noData, makeCards has --asimov, we consider them both here
        if not (getattr(args, "asimov", False) or getattr(args, "noData", False)):
            pg = self.setupPlotGroup("Data")
            self.dataGroups.append(pg)
        elif getattr(args, "asimov", False):
            pg = self.setupPlotGroup("Asimov")
            for bkgPg in self.stackGroups:
                for ds in bkgPg._datasets:
                    pg.add(ds)
            # TODO: asimov with nonzero signal strength?
            self.dataGroups.append(pg)

        resultDatasets = (res.datasets() for res in self.selectorResults)
        self.availableDatasets = reduce(lambda a, b: a | b, resultDatasets)

        resultPlots = (res.plots() for res in self.selectorResults)
        self.availablePlots = reduce(lambda a, b: a & b, resultPlots)

    def __repr__(self):
        return '<AnalysisResult instance (%d files, %d datasets, %d plots)>' % (len(self.selectorResults), len(self.availableDatasets), len(self.availablePlots))

    def __iter__(self):
        allPg = self.stackGroups + self.signalGroups + self.dataGroups
        for plotGroup in allPg:
            yield plotGroup

    def plotGroup(self, pgName):
        allPg = self.stackGroups + self.signalGroups + self.dataGroups
        for pg in allPg:
            if pg._name == pgName:
                return pg
        raise Exception("Could not find PlotGroup %s in %r" % (pgName, self))

    def setupPlotGroup(self, plotGroupName):
        plotGroup, datasetNames = parseSpecialPlotGroup(plotGroupName)
        if not plotGroup:
            if plotGroupName not in allPlotGroups:
                msg = "%s is not in the known plot group list. Check plotting/plotGroups.py" % plotGroupName
                raise Exception(msg)
            plotGroup, datasetNames = allPlotGroups[plotGroupName]

        self.putDatasetsInPlotgroup(datasetNames, plotGroup)
        return plotGroup

    def putDatasetsInPlotgroup(self, datasetNames, plotGroup):
        for datasetName in datasetNames:
            # Pick dataset from first result file that has it
            # Motivation: override a previous result for a subset
            # of datasets, allowing to reprocess a smaller number of files
            dsFound = False
            for res in self.selectorResults:
                if res.hasDataset(datasetName):
                    dsFound = True
                    # print "Info: Taking dataset %s from %r" % (datasetName, res)
                    plotGroup.add(res.getDataset(datasetName))
                    break
            if not dsFound:
                raise Exception("No dataset named %s could be found in any selectorResult" % (datasetName))
