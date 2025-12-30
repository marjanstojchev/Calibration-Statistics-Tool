import enum
import pptx
import sys
from abc import ABC, abstractmethod
import os
import numpy as np
import sys


# Mapping slide layouts
class SlideLayoutEnum(enum.IntEnum):
    SeparationSheet            = 0
    OneFieldLayout             = 1
    TwoGraphLayout             = 7
    Disclaimer                 = 5
    EndSlide                   = 6
    SensorListAndLegend        = 9
    FourGraphLayout            = 12
    FourGraphLayoutCaptions    = 11
    ThreeGraphLayoutCaptions   = 15
    OneGraphLayout             = 16
    OnlyTableLayout            = 17
    TwoGraphTxAntDiagLayout    = 13
    TwoImagesPlaceHolderLayout = 13
    StatsLimitsGroupsLayout    = 18
    TwoGraphLayoutCurves       = 19
    OneGraphLayoutsetcurves    = 20
    OneGraphLayoutstats        = 21

class StatsLimitsGroupsLayoutEnum(enum.IntEnum):
    Title    = 0
    Image1   = 1
    Text     = 2
    Image2   = 3
    Caption1 = 4
    Caption2 = 5
    Table1   = 6
    Table2   = 7

# Mapping of one field slide layout elements
class SeparationSheetEnum(enum.IntEnum):
    Title = 0
    Text  = 1

# Mapping all on one slide layout elements
class AllOnOneSlideLayoutEnum(enum.IntEnum):
    Title   = 0
    Text    = 1
    Image   = 2
    Caption = 3

# Mapping of one field slide layout elements
class OneFieldLayoutEnum(enum.IntEnum):
    TitleText = 0
    Text      = 1
    Title     = 2 

# Single legend slide layout elements mapping
class SingleLegendLayoutEnum(enum.IntEnum):
    Title     = 0
    LegendImg = 1

# Two graph layout slide elements mapping
class TwoGraphLayoutEnum(enum.IntEnum):
    Title        = 0
    PrimText     = 2
    PrimGraphImg = 1
    SecGraphImg  = 3


# Two graph layout slide elements mapping
class TwoGraphLayoutCurvesEnum(enum.IntEnum):
    Title        = 0
    PrimText     = 2
    SecGraphCap  = 5
    PrimGraphImg = 1
    PrimGraphCap = 4
    SecGraphImg  = 3
    # SecGraphCap=6
# Three graph layout slide elements mapping
class ThreeGraphLayoutCaptionsEnum(enum.IntEnum):
    Image1 = 0
    Image2 = 6
    Image3 = 7

    Title = 1
    Text  = 2

    Image1Caption = 3
    Image2Caption = 4
    Image3Caption = 5

# Four graph layout slide elements mapping
class FourGraphLayoutEnum(enum.IntEnum):
    Image1 = 2
    Image2 = 3
    Image3 = 4
    Image4 = 5

    Title         = 0
    Text          = 1
    Image1Caption = 6
    Image2Caption = 7
    Image3Caption = 8
    Image4Caption = 9

# # Four graph layout slide elements mapping
# class FourGraphLayoutCaptionsEnum(enum.IntEnum):
#     Image1 = 0
#     Image2 = 2
#     Image3 = 4
#     Image4 = 5
#     Title=1
#     Text=3


# Two graph slide for TxAnt diagrams
class TwoGraphTxAntDiagLayoutEnum(enum.IntEnum):
    Title         = 0
    Image1        = 1
    Text          = 2
    Image1Caption = 3
    Image2Caption = 4
    Image2        = 5

# Two graph slide for TxAnt diagrams
class TwoImagesPlaceholderLayoutEnum(enum.IntEnum):
    Title         = 0
    Image1        = 1
    Text          = 2
    Image1Caption = 3
    Image2Caption = 4
    Image2        = 5

# Sensor list and legend slide layout elements mapping
class SensorListAndLegendEnum(enum.IntEnum):
    Title           = 0
    Text            = 1
    LegendImg       = 2
    SensorListTable = 3
    LegendCap       = 4

# Sensor list and legend slide layout elements mapping
class OnlyTableEnum(enum.IntEnum):
    Title = 0
    Text  = 1
    Table = 2


# pptx presentation class
class Presentation:
    def __init__(self, starttemp):
        # temp = sys.modules[self.__module__].__file__
        temp = os.path.dirname(sys.argv[0])
        # temp = os.path.split(temp)
        # self.template = os.path.join(temp[0],os.path.normpath(starttemp))
        self.template = os.path.join(temp,os.path.normpath(starttemp))
        self.openStatus = True
        self.saveStatus = True
        self.invalidFileType = False
        self.openStatusString = ''
        self.saveStatusString = ''
        try:
            self.prt = pptx.Presentation(self.template)
        except Exception as e:
            self.openStatusString = 'Opening pptx: ' +str(e)
            self.openStatus = False


    # add a slide function for input slide layout
    def add_slide(self, slideLayout):
        slideLayout.setLayout(self)
        return slideLayout

    # save pptx presentation for input file name
    def save(self, pptxPath):

        # add Disclaimer
        # add end slide
        if 'combine' not in pptxPath:
            self.prt.slides.add_slide(self.prt.slide_layouts[5])
        

        # Save location processing
        # currentDir = os.path.dirname(os.path.abspath(__file__))
        currentDir = os.path.dirname(sys.argv[0])
        savePath   = os.path.join(currentDir, pptxPath)

        try:
            self.prt.save(pptxPath)
        except Exception as e:
            self.saveStatusString = e
            self.saveStatus = False



# Abstract slide layout class
class SlideLayout(ABC):
    @abstractmethod
    def setLayout(self):
        pass
    # Get info about the actual slide elements layout numbering
    def getShapesList(self):
        for shape in self.slide.placeholders:
            print('%d %s' % (shape.placeholder_format.idx, shape.name))

    def getNofGraphs(self):
        pass

# statsLimitsGroupsLayout

class StatsLimitsGroupsLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.slide    = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.StatsLimitsGroupsLayout])

        self.title    = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Title]
        self.text     = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Text]
        self.caption1 = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Caption1]
        self.caption2 = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Caption2]
        self.image1   = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Image1]
        self.image2   = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Image2]
        self.table1   = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Table1]
        self.table2   = self.slide.shapes[StatsLimitsGroupsLayoutEnum.Table2]



# All on one slide layout class
class OneGraphLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.slide   = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.OneGraphLayout])
        self.title   = self.slide.shapes[AllOnOneSlideLayoutEnum.Title]
        self.text    = self.slide.shapes[AllOnOneSlideLayoutEnum.Text]
        self.caption = self.slide.shapes[AllOnOneSlideLayoutEnum.Caption]
        self.image   = self.slide.shapes[AllOnOneSlideLayoutEnum.Image]

    def getNofGraphs(self):
        return 1

# All on one slide layout class setcurves
class OneGraphLayoutsetcurves(SlideLayout):
    def setLayout(self,Presentation):
        self.slide   = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.OneGraphLayoutsetcurves])
        self.title   = self.slide.shapes[AllOnOneSlideLayoutEnum.Title]
        self.text    = self.slide.shapes[AllOnOneSlideLayoutEnum.Text]
        self.caption = self.slide.shapes[AllOnOneSlideLayoutEnum.Caption]
        self.image   = self.slide.shapes[AllOnOneSlideLayoutEnum.Image]

    def getNofGraphs(self):
        return 1

# All on one slide layout class stats
class OneGraphLayoutstats(SlideLayout):
    def setLayout(self,Presentation):
        self.slide   = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.OneGraphLayoutstats])
        self.title   = self.slide.shapes[AllOnOneSlideLayoutEnum.Title]
        self.text    = self.slide.shapes[AllOnOneSlideLayoutEnum.Text]
        self.caption = self.slide.shapes[AllOnOneSlideLayoutEnum.Caption]
        self.image   = self.slide.shapes[AllOnOneSlideLayoutEnum.Image]

    def getNofGraphs(self):
        return 1


# Two-graph layout class
class TwoGraphLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.slide        = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.TwoGraphLayout])
        self.title        = self.slide.shapes[TwoGraphLayoutEnum.Title]
        self.primText     = self.slide.shapes[TwoGraphLayoutEnum.PrimText]
        self.primGraphImg = self.slide.shapes[TwoGraphLayoutEnum.PrimGraphImg]
        self.secGraphImg  = self.slide.shapes[TwoGraphLayoutEnum.SecGraphImg]


# Two-graph layout class Curves
class TwoGraphLayoutCurves(SlideLayout):
    def setLayout(self,Presentation):
        self.slide        = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.TwoGraphLayoutCurves])
        self.title        = self.slide.shapes[TwoGraphLayoutCurvesEnum.Title]
        self.primText     = self.slide.shapes[TwoGraphLayoutCurvesEnum.PrimText]
        self.primGraphImg = self.slide.shapes[TwoGraphLayoutCurvesEnum.PrimGraphImg]
        self.secGraphImg  = self.slide.shapes[TwoGraphLayoutCurvesEnum.SecGraphImg]
        self.primGraphCap = self.slide.shapes[TwoGraphLayoutCurvesEnum.PrimGraphCap]
        self.secGraphCap  = self.slide.shapes[TwoGraphLayoutCurvesEnum.SecGraphCap]

# One-graph layout class
class OneFieldLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.slide     =Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.OneFieldLayout])
        self.title     = self.slide.shapes[OneFieldLayoutEnum.Title]
        self.titletext = self.slide.shapes[OneFieldLayoutEnum.TitleText]
        self.text      = self.slide.shapes[OneFieldLayoutEnum.Text]

# One-graph layout class
class SeparationSheet(SlideLayout):
    def setLayout(self,Presentation):
        self.slide = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.SeparationSheet])
        self.title = self.slide.shapes[SeparationSheetEnum.Title]
        self.text  = self.slide.shapes[SeparationSheetEnum.Text]
      #   self.placeholder = self.slide.shapes[SeparationSheetEnum.Placeholder]


# Sensor-and-list layout class
class SensorListAndLegend(SlideLayout):
    def setLayout(self,Presentation):
        self.slide            = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.SensorListAndLegend])
        self.title            = self.slide.shapes[SensorListAndLegendEnum.Title]
        self.text             = self.slide.shapes[SensorListAndLegendEnum.Text]
        self.legendImg        = self.slide.shapes[SensorListAndLegendEnum.LegendImg]
        self.legendCap        = self.slide.shapes[SensorListAndLegendEnum.LegendCap]
        self.tablePlaceholder = self.slide.shapes[SensorListAndLegendEnum.SensorListTable]

class OnlyTableLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.slide            =Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.OnlyTableLayout])
        self.title            = self.slide.shapes[OnlyTableEnum.Title]
        self.text             = self.slide.shapes[OnlyTableEnum.Text]
        self.tablePlaceholder = self.slide.shapes[OnlyTableEnum.Table]

# Four-graph layout class
class FourGraphLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.imageList    = []
        self.captionsList = []
        self.slide   = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.FourGraphLayout])
        self.title   = self.slide.shapes[FourGraphLayoutEnum.Title]
        self.text    = self.slide.shapes[FourGraphLayoutEnum.Text]
        self.img1    = self.slide.shapes[FourGraphLayoutEnum.Image1]
        self.img2    = self.slide.shapes[FourGraphLayoutEnum.Image2]
        self.img3    = self.slide.shapes[FourGraphLayoutEnum.Image3]
        self.img4    = self.slide.shapes[FourGraphLayoutEnum.Image4]
        self.img1Cap = self.slide.shapes[FourGraphLayoutEnum.Image1Caption]
        self.img2Cap = self.slide.shapes[FourGraphLayoutEnum.Image2Caption]
        self.img3Cap = self.slide.shapes[FourGraphLayoutEnum.Image3Caption]
        self.img4Cap = self.slide.shapes[FourGraphLayoutEnum.Image4Caption]
        self.getImageList()
        self.getCaptionsList()

    def getImageList(self):
        self.imageList.append(self.img1)
        self.imageList.append(self.img2)
        self.imageList.append(self.img3)
        self.imageList.append(self.img4)

    def getCaptionsList(self):
        self.captionsList.append(self.img1Cap)
        self.captionsList.append(self.img2Cap)
        self.captionsList.append(self.img3Cap)
        self.captionsList.append(self.img4Cap)


    def getNofGraphs(self):
        return 4

# Three-graph layout class
class ThreeGraphLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.imageList    = []
        self.captionsList = []
        self.slide   = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.ThreeGraphLayoutCaptions])
        self.title   = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Title]
        self.text    = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Text]
        self.img1    = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Image1]
        self.img2    = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Image2]
        self.img3    = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Image3]
        self.img1Cap = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Image1Caption]
        self.img2Cap = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Image2Caption]
        self.img3Cap = self.slide.shapes[ThreeGraphLayoutCaptionsEnum.Image3Caption]

        self.getImageList()
        self.getCaptionsList()

    def getImageList(self):
        self.imageList.append(self.img1)
        self.imageList.append(self.img2)
        self.imageList.append(self.img3)

    def getCaptionsList(self):
        self.captionsList.append(self.img1Cap)
        self.captionsList.append(self.img2Cap)
        self.captionsList.append(self.img3Cap)

    def getNofGraphs(self):
        return 3

# Two-graph layout class
class TwoGraphTxAntDiagLayout(SlideLayout):
    def setLayout(self,Presentation):
        self.imageList    = []
        self.captionsList = []
        self.slide     = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.TwoGraphTxAntDiagLayout])
        self.title     = self.slide.shapes[TwoGraphTxAntDiagLayoutEnum.Title]
        self.text      = self.slide.shapes[TwoGraphTxAntDiagLayoutEnum.Text]
        self.image1    = self.slide.shapes[TwoGraphTxAntDiagLayoutEnum.Image1]
        self.image2    = self.slide.shapes[TwoGraphTxAntDiagLayoutEnum.Image2]
        self.image1Cap = self.slide.shapes[TwoGraphTxAntDiagLayoutEnum.Image1Caption]
        self.image2Cap = self.slide.shapes[TwoGraphTxAntDiagLayoutEnum.Image2Caption]

        self.getImageList()
        self.getCaptionsList()

    def getImageList(self):
        self.imageList.append(self.image1)
        self.imageList.append(self.image2)


    def getCaptionsList(self):
        self.captionsList.append(self.image1Cap)
        self.captionsList.append(self.image2Cap)

    def getNofGraphs(self):
        return 2

# Two-graph layout class
class TwoImagesPlaceHolder(SlideLayout):
    def setLayout(self,Presentation):
        self.imageList    = []
        self.captionsList = []
        self.slide     = Presentation.prt.slides.add_slide(Presentation.prt.slide_layouts[SlideLayoutEnum.TwoImagesPlaceHolderLayout])
        self.title     = self.slide.shapes[TwoImagesPlaceholderLayoutEnum.Title]
        self.text      = self.slide.shapes[TwoImagesPlaceholderLayoutEnum.Text]
        self.image1    = self.slide.shapes[TwoImagesPlaceholderLayoutEnum.Image1]
        self.image2    = self.slide.shapes[TwoImagesPlaceholderLayoutEnum.Image2]
        self.image1Cap = self.slide.shapes[TwoImagesPlaceholderLayoutEnum.Image1Caption]
        self.image2Cap = self.slide.shapes[TwoImagesPlaceholderLayoutEnum.Image2Caption]

        self.getImageList()
        self.getCaptionsList()

    def getImageList(self):
        self.imageList.append(self.image1)
        self.imageList.append(self.image2)


    def getCaptionsList(self):
        self.captionsList.append(self.image1Cap)
        self.captionsList.append(self.image2Cap)

    def getNofGraphs(self):
        return 2



# Graph list to slide mapper class, for all Rx channels together drawn graphs.
class TwoGraphConfig:
    def __init__(self, twoGraphConfig, graphAndDiagramList, diagramNr, graphList):
        self.primGraph    = 0
        self.secGraph     = 0
        self.onlyOneGraph = 0
        self.setPrimGraph(twoGraphConfig,graphAndDiagramList,diagramNr)
        self.setSecGraph(twoGraphConfig,graphAndDiagramList,diagramNr)
        self.getOnlyOneGraph(twoGraphConfig, graphList)

    # Get only one graph
    def getOnlyOneGraph(self, twoGraphConfig, graphList):
        if twoGraphConfig['primGraph'] in graphList and twoGraphConfig['secGraph'] not in graphList:
            self.onlyOneGraph = self.primGraph
        elif twoGraphConfig['primGraph'] in graphList and twoGraphConfig['secGraph']  in graphList:
            self.onlyOneGraph = 0
        elif twoGraphConfig['primGraph'] not in graphList and twoGraphConfig['secGraph'] in graphList:
            self.onlyOneGraph = self.secGraph
        else:
            self.onlyOneGraph =0

    # Set the data for the primary graphs in the two-graph layout, per one diagram nr.
    def setPrimGraph(self, twoGraphConfig, graphAndDiagramList, diagramNr):
        gdListShape = np.shape(graphAndDiagramList)
        nofGraphs   = gdListShape[0]
        nofDiagrams = gdListShape[1]
        for graphIdx in range(nofGraphs):
            for diagramIdx in range(nofDiagrams):
                if graphAndDiagramList[graphIdx][diagramIdx].graphTitle == twoGraphConfig["primGraph"] and diagramNr == graphAndDiagramList[graphIdx][diagramIdx].diagramNr:
                    self.primGraph = graphAndDiagramList[graphIdx][diagramIdx]

    # Set the data for the secondary graphs in the two-graph layout, per one diagram nr.
    def setSecGraph(self, twoGraphConfig, graphAndDiagramList, diagramNr):
        gdListShape = np.shape(graphAndDiagramList)
        nofGraphs   = gdListShape[0]
        nofDiagrams = gdListShape[1]
        for graphIdx in range(nofGraphs):
            for diagramIdx in range(nofDiagrams):
                if graphAndDiagramList[graphIdx][diagramIdx].graphTitle == twoGraphConfig["secGraph"] and diagramNr == graphAndDiagramList[graphIdx][diagramIdx].diagramNr:
                    self.secGraph = graphAndDiagramList[graphIdx][diagramIdx]

# Graph list to slide mapper class, for all Rx channels separate drawn graphs.
class TwoGraphConfigRx(TwoGraphLayout):
    def __init__(self, twoGraphConfig, graphDiagramRxChList, diagramNr, graphList):
        self.primGraphList    = []
        self.secGraphList     = []
        self.onlyOneGraphList = 0
        self.setPrimGraph(twoGraphConfig, graphDiagramRxChList, diagramNr)
        self.setSecGraph(twoGraphConfig, graphDiagramRxChList, diagramNr)
        self.getOnlyOneGraph(twoGraphConfig, graphList)

    # Get only one graph
    def getOnlyOneGraph(self, twoGraphConfig, graphList):
        if twoGraphConfig['primGraph'] in graphList and twoGraphConfig['secGraph'] not in graphList:
            self.onlyOneGraphList = self.primGraphList
        elif twoGraphConfig['primGraph'] in graphList and twoGraphConfig['secGraph'] in graphList:
            self.onlyOneGraphList = 0
        elif twoGraphConfig['primGraph'] not in graphList and twoGraphConfig['secGraph'] in graphList:
            self.onlyOneGraphList = self.secGraphList
        else:
            self.onlyOneGraphList = 0

    # Set the list for the primary graphs in the two-graph layout, per one diagram nr.
    def setPrimGraph(self, twoGraphConfig, graphDiagramRxChList, diagramNr):
        gdListShape = np.shape(graphDiagramRxChList)
        nofGraphs   = gdListShape[0]
        nofDiagrams = gdListShape[1]
        for graphIdx in range(nofGraphs):
            for diagramIdx in range(nofDiagrams):
                rxChList = graphDiagramRxChList[graphIdx][diagramIdx]
                for rxCh in range(len(rxChList)):
                    if rxChList[rxCh].graphTitle == twoGraphConfig["primGraph"] and diagramNr == rxChList[rxCh].diagramNr:
                        self.primGraphList.append(rxChList[rxCh])

    # Set the list for the secondary graphs in the two-graph layout, per one diagram nr.
    def setSecGraph(self, twoGraphConfig, graphDiagramRxChList, diagramNr):
        gdListShape = np.shape(graphDiagramRxChList)
        nofGraphs   = gdListShape[0]
        nofDiagrams = gdListShape[1]
        for graphIdx in range(nofGraphs):
            for diagramIdx in range(nofDiagrams):
                rxChList = graphDiagramRxChList[graphIdx][diagramIdx]
                for rxCh in range(len(rxChList)):
                    if rxChList[rxCh].graphTitle == twoGraphConfig["secGraph"] and diagramNr == rxChList[rxCh].diagramNr:
                        self.secGraphList.append(rxChList[rxCh])

class FourGraphConfigRx(TwoGraphLayout):

    def __init__(self, fourGraphConfig, graphDiagramRxChList, diagramNr, graphList):
        self.graphList = []
        self.setGraphList(fourGraphConfig, graphDiagramRxChList, diagramNr)

    def setGraphList(self, fourGraphConfig, graphDiagramRxChList, diagramNr):
        gdListShape = np.shape(graphDiagramRxChList)
        nofGraphs   = gdListShape[0]
        nofDiagrams = gdListShape[1]
        for graphIdx in range(nofGraphs):
            for diagramIdx in range(nofDiagrams):
                rxChList = graphDiagramRxChList[graphIdx][diagramIdx]
                for rxCh in range(len(rxChList)):
                    if rxChList[rxCh].graphTitle == fourGraphConfig["graphType"] and diagramNr == rxChList[
                        rxCh].diagramNr:
                        self.graphList.append(rxChList[rxCh])

class ThreeGraphConfigRx(TwoGraphLayout):

    def __init__(self, threeGraphConfig, graphDiagramRxChList, diagramNr, graphList):
        self.graphList = []
        self.setGraphList(threeGraphConfig, graphDiagramRxChList, diagramNr)

    def setGraphList(self, threeGraphConfig, graphDiagramRxChList, diagramNr):
        gdListShape = np.shape(graphDiagramRxChList)
        nofGraphs   = gdListShape[0]
        nofDiagrams = gdListShape[1]
        for graphIdx in range(nofGraphs):
            for diagramIdx in range(nofDiagrams):
                rxChList = graphDiagramRxChList[graphIdx][diagramIdx]
                for rxCh in range(len(rxChList)):
                    if rxChList[rxCh].graphTitle == threeGraphConfig["graphType"] and diagramNr == rxChList[
                        rxCh].diagramNr:
                        self.graphList.append(rxChList[rxCh])
