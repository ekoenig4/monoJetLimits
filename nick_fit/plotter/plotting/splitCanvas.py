import ROOT


def recursePrimitives(tobject, function, *fargs):
    function(tobject, *fargs)
    if hasattr(tobject, 'GetListOfPrimitives'):
        primitives = tobject.GetListOfPrimitives()
        if primitives:
            for item in primitives:
                recursePrimitives(item, function, *fargs)
    other_children = ['Xaxis', 'Yaxis', 'Zaxis']
    for child in other_children:
        if hasattr(tobject, 'Get'+child):
            childCall = getattr(tobject, 'Get'+child)
            recursePrimitives(childCall(), function, *fargs)


def fixFontSize(item, scale):
    if 'TH' in item.ClassName():
        return
    if item.GetName() == 'yaxis':
        item.SetTitleOffset(item.GetTitleOffset()/scale)
    sizeFunctions = ['LabelSize', 'TextSize', 'TitleSize']
    for fun in sizeFunctions:
        if hasattr(item, 'Set'+fun):
            getattr(item, 'Set'+fun)(getattr(item, 'Get'+fun)()*scale)


def readStyle(canvas):
    style = ROOT.TStyle(canvas.GetName()+"_style", "Read style")
    style.cd()
    style.SetIsReading()
    canvas.UseCurrentStyle()
    style.SetIsReading(False)
    return style


def splitCanvas(oldcanvas):
    name = oldcanvas.GetName()

    canvas = ROOT.TCanvas(name+'__new', name)
    ratioPad = ROOT.TPad('ratioPad', 'ratioPad', 0., 0., 1., .3)
    ratioPad.Draw()
    stackPad = ROOT.TPad('stackPad', 'stackPad', 0., 0.3, 1., 1.)
    stackPad.Draw()

    stackPad.cd()
    oldcanvas.DrawClonePad()
    del oldcanvas
    oldBottomMargin = stackPad.GetBottomMargin()
    stackPad.SetBottomMargin(0.)
    stackPad.SetTopMargin(stackPad.GetTopMargin()/0.7)
    canvas.SetName(name)

    ratioPad.cd()
    ratioPad.SetBottomMargin(oldBottomMargin/.3)
    ratioPad.SetTopMargin(0.)
    stack = filter(lambda p: type(p) is ROOT.THStack, stackPad.GetListOfPrimitives())[0]
    data = filter(lambda p: p.InheritsFrom("TH1") and 'data' in p.GetName().lower(), stackPad.GetListOfPrimitives())[0]
    dataOverSumMC = data.Clone(name+'_dataOverSumMC_hist')
    sumMCErrors = stack.GetHists()[0].Clone(name+'_sumMCErrors_hist')
    sumMCErrors.SetFillColorAlpha(ROOT.kGray, 0.5)
    sumMCErrors.SetMarkerSize(0)
    if len(stack.GetHists()) > 1:
        map(sumMCErrors.Add, stack.GetHists()[1:])
    dataOverSumMC.Divide(sumMCErrors)
    for i in range(data.GetNbinsX()+2):
        dataOverSumMC.SetBinError(i, data.GetBinError(i)/max(data.GetBinContent(i), 1))
        sumMCErrors.SetBinError(i, sumMCErrors.GetBinError(i)/max(sumMCErrors.GetBinContent(i), 1))
        sumMCErrors.SetBinContent(i, 1.)

    stack.GetXaxis().Copy(sumMCErrors.GetXaxis())
    sumMCErrors.GetYaxis().SetTitle('Data / #Sigma MC')
    sumMCErrors.GetYaxis().CenterTitle()
    sumMCErrors.GetYaxis().SetRangeUser(0.3, 1.7)
    sumMCErrors.GetYaxis().SetNdivisions(003)
    sumMCErrors.GetYaxis().SetTitleSize(sumMCErrors.GetYaxis().GetTitleSize()*0.65)
    sumMCErrors.GetYaxis().SetLabelSize(sumMCErrors.GetYaxis().GetLabelSize()*0.7)
    sumMCErrors.Draw("E2")
    dataOverSumMC.Draw("same")
    xaxis = dataOverSumMC.GetXaxis()
    line = ROOT.TLine(xaxis.GetBinLowEdge(xaxis.GetFirst()), 1, xaxis.GetBinUpEdge(xaxis.GetLast()), 1)
    line.SetLineStyle(ROOT.kDotted)
    line.Draw()

    # Removes the '0' from bottom axis since it usually clashes with ratio labels
    if not stackPad.GetLogy():
        firstPrimitive = filter(lambda p: p.InheritsFrom("TH1"), stackPad.GetListOfPrimitives())[0]
        firstPrimitive.SetMinimum(firstPrimitive.GetMaximum()*1.e-5)

    recursePrimitives(stackPad, fixFontSize, 1/0.7)
    stackPad.Modified()
    recursePrimitives(ratioPad, fixFontSize, 1/0.3)
    ratioPad.Modified()
    canvas.Update()

    ROOT.SetOwnership(stackPad, False)
    # stackPad already owns primitives
    ROOT.SetOwnership(ratioPad, False)
    for obj in ratioPad.GetListOfPrimitives():
        ROOT.SetOwnership(obj, False)
    ratioPad.GetListOfPrimitives().SetOwner(True)
    canvas.cd()
    canvas.GetListOfPrimitives().SetOwner(True)
    return canvas
