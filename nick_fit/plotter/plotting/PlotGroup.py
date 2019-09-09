import styles
import math


class PlotGroup:
    Stackable, SignalLike, Data = range(3)

    def __init__(self, name, title, groupType=Stackable):
        self._name = name
        self._title = title
        self._type = groupType
        self._datasets = []
        self._shapeCache = {}
        if self._name in styles.styles:
            self._style = styles.styles[self._name]
        elif self._type == self.SignalLike:
            self._style = None
        else:
            print "Warning: No style info for %s" % repr(self)
            self._style = None

    def __repr__(self):
        return '<PlotGroup instance ("%s", "%s")>' % (self._name, self._title)

    def plotType(self):
        return self._type

    def hasStyle(self):
        return self._style is not None

    def add(self, dataset_or_datasets):
        if type(dataset_or_datasets) is list:
            self._datasets.extend(dataset_or_datasets)
        else:
            self._datasets.append(dataset_or_datasets)

    def applyStyle(self, plot):
        if self.hasStyle():
            styles.copyStyle(self._style, plot)

    def getPlot(self, plotName, callback=None):
        if len(self._datasets) == 0:
            raise Exception("%s has no datasets, but getPlot() called." % repr(self))

        plot = self._datasets[0].getPlot(plotName).Clone("tmptmp")
        # Somehow, if the first plot accessed in the session does not
        # have a sumw2 vector, all subsequent ones don't work?!
        # So, force the issue at the expense of lots of RuntimeWarnings
        plot.Sumw2()

        if len(self._datasets) > 1:
            for i in range(1, len(self._datasets)):
                plot.Add(self._datasets[i].getPlot(plotName))

        if callback:
            plot = callback(plot)
        plot.SetName("%s__%s" % (plotName, self._name))
        plot.SetTitle(self._title)
        self.applyStyle(plot)
        return plot

    def buildConfidenceIntervalFromToys(self, toyHist, yRange, coverage):
        # Make hists with appropriate axis
        shapeUp = toyHist.ProjectionX("tmp1", 1, 1)
        shapeUp.Reset()
        shapeDown = shapeUp.Clone("tmp2")
        for xBin in range(toyHist.GetNbinsX()+2):
            vals = []
            # Account for ROOT's bin index
            for yBin in range(yRange[0]+1, yRange[1]+2):
                vals.append(toyHist.GetBinContent(xBin, yBin))
            vals.sort()
            plus1Sigma = min(len(vals)-1, int((0.5+coverage/2.)*len(vals)))
            shapeUp.SetBinContent(xBin, vals[plus1Sigma])
            minus1Sigma = max(0, int((0.5-coverage/2.)*len(vals)))
            shapeDown.SetBinContent(xBin, vals[minus1Sigma])

        return (shapeUp, shapeDown)

    def buildConfidenceIntervalFromHessian(self, hessHist):
        # Make hists with appropriate axis
        shapeUp = hessHist.ProjectionX("tmp1", 1, 1)
        shapeUp.Reset()
        shapeDown = shapeUp.Clone("tmp2")
        for xBin in range(hessHist.GetNbinsX()+2):
            vals = []
            # Account for ROOT's bin index
            for yBin in range(10, 110+1):
                vals.append((hessHist.GetBinContent(xBin, yBin)-hessHist.GetBinContent(xBin, 1))**2)
            sigma = math.sqrt(sum(vals))
            shapeUp.SetBinContent(xBin, hessHist.GetBinContent(xBin, 1) + sigma)
            shapeDown.SetBinContent(xBin, hessHist.GetBinContent(xBin, 1) - sigma)

        return (shapeUp, shapeDown)

    def getShape(self, shapeHistName, systematicName, callback):
        ''' Returns tuple of (up, down) or (nominal, ) or () if in error '''
        if shapeHistName not in self._shapeCache.keys():
            self._shapeCache[shapeHistName] = (self.getPlot(shapeHistName+"_systs"), self.getPlot(shapeHistName+"_lheWeights"))
        shapeHist, lheWeightsHist = self._shapeCache[shapeHistName]

        if systematicName is None:
            # Nominal
            shape = shapeHist.ProjectionX("tmp", 1, 1)
            if callback:
                shape = callback(shape)
            return (shape, )
        elif systematicName == 'pdf':
            # Most datasets will have weights 9 - 109 associated with the 100 NNPDF replicas
            # In case a PlotGroup has more than one dataset with incompatible LHE weights layout
            # this will produce garbage...
            nnpdfReplicasRange = (8, 110)
            shapeUp, shapeDown = self.buildConfidenceIntervalFromToys(lheWeightsHist, nnpdfReplicasRange, 0.682)
        elif systematicName == 'pdfHess':
            shapeUp, shapeDown = self.buildConfidenceIntervalFromHessian(lheWeightsHist)
        elif systematicName == 'alphaS':
            # Alpha_s is last two NNPDF sets in most samples (110, 111)
            # +1 to account for ROOT histogram offset
            shapeUp = lheWeightsHist.ProjectionX("tmp1", 110, 110)
            shapeDown = lheWeightsHist.ProjectionX("tmp2", 111, 111)
        elif systematicName == 'factRenormScale':
            # Almost all datasets will have weights 0 - 8 associated with the Factorisation and
            # Renormalisation scale variations.
            yRange = (0, 8)
            shapeUp, shapeDown = self.buildConfidenceIntervalFromToys(lheWeightsHist, yRange, 1.)
        else:
            # Find bin for systematic
            upBin, downBin = None, None
            for i in range(shapeHist.GetNbinsY()+2):
                binName = shapeHist.GetYaxis().GetBinLabel(i)
                if binName == systematicName+"Up":
                    upBin = i
                elif binName == systematicName+"Down":
                    downBin = i
            if upBin is None or downBin is None:
                msg = "Systematic name %s does not exist in for shapeHist %s in %r" % (systematicName, shapeHistName, self)
                raise Exception(msg)
            shapeUp = shapeHist.ProjectionX("tmp1", upBin, upBin)
            shapeDown = shapeHist.ProjectionX("tmp2", downBin, downBin)
        if callback:
            shapeUp = callback(shapeUp)
            shapeDown = callback(shapeDown)
        return (shapeUp, shapeDown)
