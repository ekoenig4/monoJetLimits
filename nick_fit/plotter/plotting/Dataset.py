import crossSections


class Dataset:
    def __init__(self, resultDirectory, luminosity):
        self._dir = resultDirectory
        self._name = resultDirectory.GetName()

        self._plots = []
        for key in self._dir.GetListOfKeys():
            if "TH" in key.GetClassName() and key.GetName() != "counters":
                self._plots.append(key.GetName())

        self._lumi = luminosity

        # If exists -> True, if None -> False
        self._isMC = (resultDirectory.Get("isMC/Yes") != None)

        self._counters = resultDirectory.Get("counters")

        reweightDataset = resultDirectory.Get("referenceSample")
        if reweightDataset != None:
            # This is a DM reweighted sample, so the cross section is taken
            # from the fullsim sample that the reweighted sample is derived from
            self._crossSection = crossSections.crossSections[reweightDataset.GetTitle()]
            # FIXME: temporary workaround, isMC folder not in result directory
            self._isMC = True
        elif self._name in crossSections.crossSections:
            self._crossSection = crossSections.crossSections[self._name]
        elif self._isMC:
            print "Warning: Missing cross section for %s, using 1 pb" % repr(self)
            self._crossSection = 1.
        # print "Info: %s effective lumi: %.2f /fb" % (self._name, self.getEffectiveLumi()/1000.)

    def __repr__(self):
        return '<Dataset instance ("%s")>' % self._name

    def isValid(self):
        if self._counters == None:
            return False
        selectorCounter = self._dir.Get("selectorCounter")
        if selectorCounter == None:
            return False
        if selectorCounter.GetBinContent(1) == 0:
            print "Info: %r has zero entries in selectorCounter, excluding" % self
            return False
        return True

    def plots(self):
        return self._plots

    def setCrossSection(self, newXs):
        self._crossSection = newXs

    def getNormalization(self):
        norm = 1.
        if self._isMC:
            sumWeights = self._counters.GetBinContent(3) - self._counters.GetBinContent(2)
            norm = self._crossSection * self._lumi / sumWeights
        if 'ADD' in self._name:
            # Truncation info is in weightsMonitor
            wm = self._dir.Get('weightsMonitor')
            if not wm.GetXaxis().GetBinLabel(1+3) == 'GenCutsWeight':
                raise Exception("Something's wrong with ADD")
            norm *= wm.GetBinContent(1+2)/wm.GetBinContent(1+3)
        return norm

    def getEffectiveLumi(self):
        if not self._isMC:
            return self._lumi
        npos = self._counters.GetBinContent(3)
        nneg = self._counters.GetBinContent(2)
        sumw = npos - nneg
        sumw2 = npos + nneg  # Assuming all weights +/- 1
        return sumw**2 / sumw2 / self._crossSection

    def getPlot(self, plotName):
        hist = self._dir.Get(plotName)
        if not hist:
            raise Exception("No plot named %s in %s" % (plotName, repr(self)))

        hist.SetName("%s__%s" % (plotName, self._name))
        hist.Scale(self.getNormalization())
        hist.UseCurrentStyle()
        return hist
