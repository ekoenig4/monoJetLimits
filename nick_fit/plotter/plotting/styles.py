import ROOT


def forceStyle():
    style = ROOT.gROOT.GetStyle("MonoZ")
    if style != None:
        style.cd()
        return
    style = ROOT.gROOT.GetStyle("Plain").Clone("MonoZ")
    ROOT.SetOwnership(style, False)

    style.SetOptStat(0)
    style.SetOptTitle(0)

    style.SetCanvasDefH(600)
    style.SetCanvasDefW(600)
    style.SetPadTopMargin(0.07)
    style.SetPadBottomMargin(0.13)
    style.SetPadLeftMargin(0.14)
    style.SetPadRightMargin(0.04)

    style.SetTitleFont(42, "XYZ")
    style.SetTitleSize(0.05, "XYZ")
    style.SetTitleXOffset(0.9)
    style.SetTitleYOffset(1.25)

    style.SetLabelFont(42, "XYZ")
    style.SetLabelOffset(0.007, "XYZ")
    style.SetLabelSize(0.03, "XYZ")

    style.SetPadTickX(1)
    style.SetPadTickY(1)

    style.SetLegendFont(42)
    style.SetLegendBorderSize(0)

    style.GetAttDate().SetTextFont(42)
    style.GetAttDate().SetTextColor(ROOT.kGray)

    style.cd()


def getColor(c):
    return ROOT.TColor.GetColor(c)


def getColorLight(c):
    if type(c) is str:
        return ROOT.TColor.GetColorLight(getColor(c))
    return ROOT.TColor.GetColorLight(c)


def getColorDark(c):
    if type(c) is str:
        return ROOT.TColor.GetColorDark(getColor(c))
    return ROOT.TColor.GetColorDark(c)


def copyStyle(style, plot):
    if style["fill"]:
        style["fill"].Copy(plot)
    if style["line"]:
        style["line"].Copy(plot)
    if style["marker"]:
        style["marker"].Copy(plot)


styles = {
    "Nonresonant":
        {
            "fill": ROOT.TAttFill(getColor("#FFCC33"), 1001),
            "line": ROOT.TAttLine(getColorDark("#FFCC33"), ROOT.kSolid, 1),
            "marker": None,
        },
    "DYTauTau":
        {
            "fill": ROOT.TAttFill(ROOT.kMagenta, 1001),
            "line": ROOT.TAttLine(getColorDark(ROOT.kMagenta), ROOT.kSolid, 1),
            "marker": None,
        },
    "ZZ2l2nu":
        {
            "fill": ROOT.TAttFill(ROOT.kGreen+1, 1001),
            "line": ROOT.TAttLine(getColorDark(ROOT.kGreen+1), ROOT.kSolid, 1),
            "marker": None,
        },
    "WZ3lnu":
        {
            "fill": ROOT.TAttFill(getColor("#6799FF"), 1001),
            "line": ROOT.TAttLine(getColorDark("#6799FF"), ROOT.kSolid, 1),
            "marker": None,
        },
    "ZZ4l":
        {
            "fill": ROOT.TAttFill(getColor("#00CC66"), 1001),
            "line": ROOT.TAttLine(getColorDark("#00CC66"), ROOT.kSolid, 1),
            "marker": None,
        },
    "Other2l":
        {
            "fill": ROOT.TAttFill(ROOT.kGray+1, 1001),
            "line": ROOT.TAttLine(getColorDark(ROOT.kGray+1), ROOT.kSolid, 1),
            "marker": None,
        },
    "DrellYan":
        {
            "fill": ROOT.TAttFill(getColor("#FF99CB"), 1001),
            "line": ROOT.TAttLine(getColorDark("#FF99CB"), ROOT.kSolid, 1),
            "marker": None,
        },
    "DrellYanEWK":
        {
            "fill": ROOT.TAttFill(getColor("#0099CB"), 1001),
            "line": ROOT.TAttLine(getColorDark("#0099CB"), ROOT.kSolid, 1),
            "marker": None,
        },
    "WJets":
        {
            "fill": ROOT.TAttFill(getColor("#FFFF02"), 1001),
            "line": ROOT.TAttLine(getColorDark("#FFFF02"), ROOT.kSolid, 1),
            "marker": None,
        },
    "Data":
        {
            "fill": None,
            "line": None,
            "marker": ROOT.TAttMarker(ROOT.kBlack, ROOT.kFullCircle, 0.7),
        },
    "Signal0":
        {
            "fill": None,
            "line": ROOT.TAttLine(ROOT.kRed+1, ROOT.kSolid, 2),
            "marker": None,
        },
    "Signal1":
        {
            "fill": None,
            "line": ROOT.TAttLine(ROOT.kMagenta+1, ROOT.kSolid, 2),
            "marker": None,
        },
    "Signal2":
        {
            "fill": None,
            "line": ROOT.TAttLine(ROOT.kBlack, ROOT.kSolid, 2),
            "marker": None,
        },
    "Signal3":
        {
            "fill": None,
            "line": ROOT.TAttLine(ROOT.kRed+1, ROOT.kDashed, 2),
            "marker": None,
        },
    "Signal4":
        {
            "fill": None,
            "line": ROOT.TAttLine(ROOT.kMagenta+1, ROOT.kDashed, 2),
            "marker": None,
        },
    "MCUncertainty":
        {
            "fill": ROOT.TAttFill(ROOT.kGray+2, 3013),
            "line": ROOT.TAttLine(ROOT.kWhite, 0, 0),
            "marker": ROOT.TAttMarker(ROOT.kWhite, 0, 0),
        },
}
