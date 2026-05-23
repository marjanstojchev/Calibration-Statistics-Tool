
import load_TxAntData as ld
import powerpoint as pp
import os
import numpy as np
import pptx
import logconfig as log
import txantdiag_data_processing as dp
import txantdiag_plotdata as plt
import sys
import auxiliary as aux
from pptx import Presentation
import yaml

bUseGui = True

lenofargs = len(sys.argv);
if( lenofargs == 1): # ptu file / pfad hier vorgeben ( als erstes argument in sys.argv ist immer die script datei selbst enthalten)
    absPath = r'C:\Arbeit\TxAntDiagram'
    absPath =r'C:\Arbeit\ALPSsample'
    absPath=r'\\ad.smartmicro.de\Data\Messdaten\MDSMS0\Kalibrierung\Test_RR_Kalibrierung\UMRR-96_Type153\2019-05-07_40 x umrr96_T153_kammer1\OK'
    absPath=r'C:\OpenAccess\vonAndreasA\Typ132Daten'
    absPath=r'C:\Arbeit\tabelaTest'
    absPath =r'C:\Arbeit\ALPSsample\UMRR-98.00.00-0002E74A'
    absPath =r'C:\StatisticToolPython_QtGUI_CT_Branch\Data\UMRR-98.00.00-0002E72A'
    # absPath =r'C:\StatisticToolPython_QtGUI_CT_Branch\Data\levelcheck\Typ_0x84XXXX_UMRR-11\2019\intern_5xUMRR-110004-840100ohneLogo20erApr2019'
    # absPath = r'C:\Arbeit\test'
    # absPath=r'C:\Arbeit\noTxAnt\noDiag'

elif(lenofargs == 2): # als argument einzelner pfad oder ptu file  ( als erstes argument in sys.argv ist immer die script datei selbst enthalten)
    absPath = sys.argv[1]
#else:  # liste von dateien
    absPath = list(sys.argv[1:])


plotSetup = {

    'useSensorMuster': 0,
    'sensorMusterList': [],
    'targetAngle': 0,  # Show in target angle.
    'upsideDown': 0,  # Sensor is upside down mounted: 1, otherwise: 0.
    'AzDiag': 1,  # Generate azimuth diagrams using azimuth angle
    'ElDiag': 1, # Generate elevation diagrams using elevation angle

    'xScaleSizeAuto': 0,  # Automatic size of the xScale: 1, manual setup with xScaleSizeAz and xScaleSizeEl: 0.
    'xScaleSizeAz': 90, # (+-°) Size of the xScaleSizeAz, when xAxisAuto = 0.
    'xScaleSizeEl': 45, # (+-°) Size of the xScaleSizeEl, when xAxisAuto = 0.

    'imageDpi': 220, # Set plot image resolution
    'nofSensorMeasToShow': 32,  # The max number of sensor measurements to show

    'plotOrigGraphs':1, # Plot original (not normalised) graphs: 1, otherwise: 0.
    'plotNormGraphs':1, # Plot normalised graphs: 1, otherwise: 0.

    'graphsPerSlide': 1 # 1 - one graph per slide, 2 - two graph per slide, 3 - three graph per slide, 4 - four graph per slide, else - invalid.
}

# Generate graph setup
graphConfig = {
    # Power level diagrams
    'level': 1,  # Corrected transmited Power level using spectrum analyser [dBm].
    'levelPowMet': 0,  # Corrected transmited Power level using powermeter [dBm].

    'levelMeasSpec': 0,  # Measured transmited Power level using spectrum analyser [dBm].
    'levelMeasPowMet': 0, # Measured transmited Power level using spectrum analyser [dBm].

    # Phase difference diagrams
    'frequency': 0,  # Actual frequency [MHz].
    'time': 0,  # Time [ms].

}

# Start data evaluation
def start_data_evaluation(parsedDataList, plotSetup, graphConfig, txAntDiagLogger, output_pathpptx, pptxTitle, starttemp):
    # Output path
    outputPath = aux.txAntDiagOutputPath

    # Create directory if doesnt exist
    crDirStatus, crDirErrorString = aux.createDirectory(outputPath)

    myLogger = txAntDiagLogger.logger
    myLogger.info('Starting.')

    if not crDirStatus:
        myLogger.error(crDirErrorString)
        return

    # Clear the output folder
    clearDataStatus, clearDataString = aux.clearAll(aux.txAntDiagOutputPath)
    if not clearDataStatus:
        myLogger.error(clearDataString)
        return


    if len(parsedDataList) == 0:
        # pptx. save path
        pptxPath = os.path.join(output_pathpptx,pptxTitle)
        prs = pp.Presentation(starttemp)
        of_layout = pp.OneFieldLayout()
        ss_layout = pp.SeparationSheet()
        myLogger.error('No parsed Tx Antenna Diagram files found!')
        
        # Copying the LogFile to the output directory
        logFileOutputPath = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.TxAntDiagrams.value)
        status,errorSting = aux.copyFile(log.txAntDiagLogFilePath, logFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)
        loadDataLogFileOutputPath = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.MainLoadData.value)
        status, errorSting = aux.copyFile(log.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
        if not  status:
            myLogger.warning(errorSting)
        
        # reading log files
        log_file = log.txAntDiagLogFilePath
        with open(log_file, 'r') as logmessages:
            content = logmessages.readlines()
            error_mesg = 0
            warning_mesg = 0
            for line in content:
                if 'ERROR' in line:
                    error_mesg += 1
                if 'WARN' in line:
                    warning_mesg += 1
        
        # error messages
        of_layout = prs.add_slide(of_layout)
        of_layout.title.text = 'Tx Antenna Diagrams'
        of_layout.titletext.text = 'Warnings and Errors'
        of_layout.text.text = 'Total Number of Warning messages: ' + str(warning_mesg) + '\n' + \
            'Total Number of Error messages: ' + str(error_mesg)
        
        # sepration sheet
        ss_layout = prs.add_slide(ss_layout)
        ss_layout.title.text = 'Tx Antenna Diagrams'
        ss_layout.text.text  = 'Tx Antenna Diagrams'
        prs.save(pptxPath)
        return


    # # Load Data by absolute path
    # myLogger.info('Loading data.')
    # loadedData = ld.LoadData(absPath)

    # Title of the generated output .pptx file
    # pptxTitle = 'TxAnt_Diagrams.pptx'

    # pptx. save path
    pptxPath = os.path.join(output_pathpptx,pptxTitle)

    # Initialise PowerPoint presentation and specific layout objects
    prs = pp.Presentation(starttemp)
    if prs.openStatus == False:
        myLogger.error(prs.openStatusString)
        return
    else:
        myLogger.info('PPTX writing starts: ' +pptxTitle)
        of_layout  = pp.OneFieldLayout()
        ss_layout  = pp.SeparationSheet()
        og_layout  = pp.OneGraphLayout()
        tg_layout  = pp.TwoGraphTxAntDiagLayout()
        fg_layout  = pp.FourGraphLayout()
        trg_layout = pp.ThreeGraphLayout()
        ll_layout  = pp.SensorListAndLegend()
        rt_layout  = pp.OnlyTableLayout()
    
    # List of all configured graph types
    graphList = dp.getGraphList(graphConfig)

    if len(graphList) == 0:
        
        myLogger.error('No graphs configured!')
        # Copying the LogFile to the output directory
        logFileOutputPath  = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.TxAntDiagrams.value)
        status, errorSting = aux.copyFile(log.txAntDiagLogFilePath, logFileOutputPath)
        if not status:
            myLogger.warning(errorSting)
        loadDataLogFileOutputPath = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.MainLoadData.value)
        status, errorSting = aux.copyFile(log.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
        if not status:
            myLogger.warning(errorSting)
        return


    # List of sensors found
    # sensorList=dp.getSensorList(antTypeIdx,loadedData)

    # # List of measurement date and time
    # dateAndTimeList=dp.getDateAndTimeList(loadedData)

    #list of date-time and sensor comnbination
    dateTimeSensorCombList = dp.getDateTimeSensorCombList(parsedDataList)

    if len(dateTimeSensorCombList) != 0:
        myLogger.info('Num. of Sensor - Date and Time Comb.: ' +str(len(dateTimeSensorCombList)) + '.')
    else:
        myLogger.error('Empty Date/Time - Sensor combination list!')


    # Tx Antenna list
    txAntList = dp.getTxAntList(parsedDataList)
    if len(txAntList) == 0:
        # Copying the LogFile to the output directory
        myLogger.error('No Tx - Antennas found!')
        logFileOutputPath  = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.TxAntDiagrams.value)
        status, errorSting = aux.copyFile(log.txAntDiagLogFilePath, logFileOutputPath)
        if not status:
            myLogger.warning(errorSting)
        loadDataLogFileOutputPath = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.MainLoadData.value)
        status, errorSting = aux.copyFile(log.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
        if not status:
            myLogger.warning(errorSting)
        return

    # reading log files
    log_file = log.txAntDiagLogFilePath
    with open(log_file, 'r') as logmessages:
        content = logmessages.readlines()
        error_mesg = 0
        warning_mesg = 0
        for line in content:
            if 'ERROR' in line:
                error_mesg += 1
            if 'WARN' in line:
                warning_mesg += 1
    
    # error messages
    of_layout = prs.add_slide(of_layout)
    of_layout.title.text = 'Tx Antenna Diagrams'
    of_layout.titletext.text = 'Warnings and Errors'
    of_layout.text.text = 'Total Number of Warning messages: ' + str(warning_mesg) + '\n' + \
        'Total Number of Error messages: ' + str(error_mesg)
    
    # sepration sheet
    ss_layout = prs.add_slide(ss_layout)
    ss_layout.title.text = 'Tx Antenna Diagrams'
    ss_layout.text.text  = 'Tx Antenna Diagrams'
    
    # Get the scaling parameters for each graph
    lowerMarginDict = dict()
    normLowerMarginDict = dict()
    # lowerMarginDictList=[]

    upperMarginDict = dict()
    normUpperMarginDict = dict()
    # upperMarginDictList =[]

    centFreqDictList = []

    normAxisAvgAngDictList = []

    if len(dateTimeSensorCombList) != 0:

        # Generate legend for sensor plot lines colors
        plt.generateLegend(plotSetup, dateTimeSensorCombList)

        if(plotSetup['plotOrigGraphs'] == 1):

            for graphIdx in range(len(graphList)):
                    normGraphs = 0
                    lowerMargin = plt.scaleLowerMargin(graphList[graphIdx], parsedDataList,normGraphs)

                    lowerMarginEntry = {graphList[graphIdx]: lowerMargin}
                    lowerMarginDict.update(lowerMarginEntry)

                    upperMargin = plt.scaleUpperMargin(graphList[graphIdx], parsedDataList,normGraphs)

                    upperMarginEntry = {graphList[graphIdx]: upperMargin}
                    upperMarginDict.update(upperMarginEntry)

        if(plotSetup['plotNormGraphs'] == 1):

            for graphIdx in range(len(graphList)):
                    normGraphs  = 1
                    lowerMargin = plt.scaleLowerMargin(graphList[graphIdx], parsedDataList,normGraphs)

                    lowerMarginEntry = {graphList[graphIdx]: lowerMargin}
                    normLowerMarginDict.update(lowerMarginEntry)

                    upperMargin = plt.scaleUpperMargin(graphList[graphIdx], parsedDataList,normGraphs)

                    upperMarginEntry = {graphList[graphIdx]: upperMargin}
                    normUpperMarginDict.update(upperMarginEntry)

        for txAntIdx in range(len(txAntList)):
            centFreqDict = dict()
            normAxisAvgAngDict = dict()

            # Get center frequency values
            avgFreq = dp.getAvgFreqPerTxAnt(txAntList[txAntIdx], parsedDataList)
            minFreq = dp.getMinFreqPerTxAnt(txAntList[txAntIdx], parsedDataList)
            maxFreq = dp.getMaxFreqPerTxAnt(txAntList[txAntIdx], parsedDataList)

            posFreqDev = maxFreq - avgFreq
            negFreqDev = avgFreq - minFreq
            avgFreqGHz = avgFreq / 1e3 # MHz to GHz

            posFreqDevTemp = posFreqDev*10000
            negFreqDevTemp = posFreqDev*10000
            avgFreqTemp    = avgFreqGHz*100

            posFreqDevTemp = int(posFreqDevTemp) #format (MHz)
            negFreqDevTemp = int(negFreqDevTemp) #format (MHz)
            avgFreqTemp    = int(avgFreqTemp)

            posFreqDevMHz = posFreqDevTemp /10000
            negFreqDevMHz = negFreqDevTemp /10000
            avgFreqGHz    = avgFreqTemp /100

            centFreqDict.update({'avgFreqGHz': avgFreqGHz, 'posFreqDevMHz': posFreqDevMHz, 'negFreqDevMHz': negFreqDevMHz})
            centFreqDictList.append(centFreqDict)

            normAxisAvgAngAz = dp.getNormAxisAvgAngPerTxAnt(txAntList[txAntIdx], parsedDataList, 'Az')
            normAxisAvgAngAz = format(normAxisAvgAngAz, '.4f')

            normAxisAvgAngEl = dp.getNormAxisAvgAngPerTxAnt(txAntList[txAntIdx], parsedDataList, 'El')
            normAxisAvgAngEl = format(normAxisAvgAngEl, '.4f')

            normAxisAvgAngDict.update({'Az': normAxisAvgAngAz, 'El':normAxisAvgAngEl})
            normAxisAvgAngDictList.append(normAxisAvgAngDict)

        if 'combine' not in starttemp:
            # Sensor List and Legend slide
            llSlide = prs.add_slide(og_layout)
            llSlide.title.text = 'Tx Antenna Diagrams'

            legendTitle = plt.legFigTitle
            legendPath  = os.path.join(outputPath, legendTitle)
            llSlide.image.insert_picture(legendPath)
            llSlide.title.text = 'Tx Antenna Diagrams'
            llSlide.text.text  = 'Legend'

            # add total number of protocol tables
            ot_slide = prs.add_slide(rt_layout)
            ot_slide.title.text = 'Tx Antenna Diagrams'
            # Sensor list reshaping for listing in a table
            dateTimeSensorCombTable = dateTimeSensorCombList.copy()
            nofSensorMeas = len(dateTimeSensorCombTable)

            if nofSensorMeas > plotSetup['nofSensorMeasToShow']:
                dateTimeSensorCombTable = dateTimeSensorCombTable[:plotSetup['nofSensorMeasToShow']]
                nofSensorMeas = len(dateTimeSensorCombTable)

            maxNofRows = 16

            nofColsFirstSlide = 2
            maxNofSensorMeasFirstSlide = nofColsFirstSlide * maxNofRows

            nofColsRestSlides = 3
            maxNofSensorMeasRestSlides = nofColsRestSlides * maxNofRows

            sensorMeasFirstSlideList = dateTimeSensorCombTable

            nofRowsFirstSlide = maxNofRows
            nofRowsRestSlides = maxNofRows
            nofRestTables = 0

            if nofSensorMeas <= maxNofSensorMeasFirstSlide:
                if nofSensorMeas % nofColsFirstSlide == 0:
                    nofRowsFirstSlide = int(nofSensorMeas / nofColsFirstSlide)
                    sensorMeasFirstSlideList = np.reshape(sensorMeasFirstSlideList,
                                                        (nofRowsFirstSlide, nofColsFirstSlide))
                else:
                    dateTimeSensorCombTable.append('')
                    nofRowsFirstSlide = int(nofSensorMeas / nofColsFirstSlide) + 1
                    sensorMeasFirstSlideList = np.reshape(sensorMeasFirstSlideList,
                                                        (nofRowsFirstSlide, nofColsFirstSlide))
                # Table insertion
                firstSlideTablePlaceholder = ot_slide.tablePlaceholder
                firstSlideTablePlaceholder = firstSlideTablePlaceholder.insert_table(rows=nofRowsFirstSlide, cols=nofColsFirstSlide)
                firstSlideTablePlaceholder = firstSlideTablePlaceholder.table

                ot_slide.text.text = 'Sensor measurements list: 1 - ' + str(nofSensorMeas)

                # Table filling
                for row in range(nofRowsFirstSlide):
                    for col in range(nofColsFirstSlide):
                        cell = firstSlideTablePlaceholder.cell(row, col)
                        textFrame = cell.text_frame
                        paragraph = textFrame.paragraphs[0]
                        run = paragraph.add_run()
                        if sensorMeasFirstSlideList[row, col] != '':
                            run.text = sensorMeasFirstSlideList[row, col]['dateAndTime'] + '_' + \
                                    sensorMeasFirstSlideList[row, col]['sensor']
                            # run.text = sensorMeasFirstSlideList[row, col]
                        font = run.font
                        font.size = pptx.util.Pt(16)
                myLogger.info('Sensors list table and legend slide inserted.')
            else:

                sensorMeasFirstSlideList = dateTimeSensorCombTable[:maxNofSensorMeasFirstSlide]
                sensorMeasFirstSlideList = np.reshape(sensorMeasFirstSlideList,
                                                    (nofRowsFirstSlide, nofColsFirstSlide))

                # Table insertion
                firstSlideTablePlaceholder = ot_slide.tablePlaceholder
                firstSlideTablePlaceholder = firstSlideTablePlaceholder.insert_table(rows=nofRowsFirstSlide,
                                                                                    cols=nofColsFirstSlide)
                firstSlideTablePlaceholder = firstSlideTablePlaceholder.table

                ot_slide.text.text = 'Sensor measurements list: 1 - ' + str(maxNofSensorMeasFirstSlide)

                # Table filling
                for row in range(nofRowsFirstSlide):
                    for col in range(nofColsFirstSlide):
                        cell = firstSlideTablePlaceholder.cell(row, col)
                        textFrame = cell.text_frame
                        paragraph = textFrame.paragraphs[0]
                        run = paragraph.add_run()
                        if sensorMeasFirstSlideList[row, col] != '':
                            run.text = sensorMeasFirstSlideList[row, col]['dateAndTime'] + '_' + \
                                    sensorMeasFirstSlideList[row, col]['sensor']
                            # run.text = sensorMeasFirstSlideList[row, col]
                        font = run.font
                        font.size = pptx.util.Pt(16)

                nofRestTables = int( np.ceil((nofSensorMeas - maxNofSensorMeasFirstSlide) / maxNofSensorMeasRestSlides))

                sensorMeasRestLists = []
                sensorMeasRestWholeList = dateTimeSensorCombTable[maxNofSensorMeasFirstSlide:]

                for i in range(nofRestTables):
                    # Rest Tables insertion
                    rtSlide = prs.add_slide(rt_layout)
                    rtSlide.title.text = 'Antenna system diagrams - Type '

                    start = i * maxNofSensorMeasRestSlides
                    stop  = start + maxNofSensorMeasRestSlides
                    sensorMeasRestList = sensorMeasRestWholeList[start:stop]

                    if i != (nofRestTables - 1):
                        rtSlide.text.text = 'Sensor measurements list: ' + str(
                            start + maxNofSensorMeasFirstSlide + 1) + ' - ' + str(
                            stop + maxNofSensorMeasFirstSlide)
                        sensorMeasRestList = np.reshape(sensorMeasRestList,
                                                        (nofRowsRestSlides, nofColsRestSlides))

                    else:

                        rtSlide.text.text = 'Sensor measurements list: ' + str(
                            start + maxNofSensorMeasFirstSlide + 1) + ' - ' + str(
                            start + len(sensorMeasRestList) + maxNofSensorMeasFirstSlide)

                        residual = len(sensorMeasRestList) % nofColsRestSlides

                        if (residual) == 0:
                            nofRowsRestSlides  = int(len(sensorMeasRestList) / nofColsRestSlides)
                            sensorMeasRestList = np.reshape(sensorMeasRestList,
                                                            (nofRowsRestSlides, nofColsRestSlides))
                        else:
                            nofRowsRestSlides  = int(len(sensorMeasRestList) / nofColsRestSlides) + 1

                            for j in range(nofColsRestSlides - residual):
                                sensorMeasRestList.append('')

                            sensorMeasRestList = np.reshape(sensorMeasRestList,
                                                            (nofRowsRestSlides, nofColsRestSlides))

                    dim = np.shape(sensorMeasRestList)
                    nofRowsRestSlides = dim[0]

                    restSlidesTablePlaceholder = rtSlide.tablePlaceholder
                    restSlidesTablePlaceholder = restSlidesTablePlaceholder.insert_table(rows=nofRowsRestSlides,
                                                                                        cols=nofColsRestSlides)
                    restSlidesTablePlaceholder = restSlidesTablePlaceholder.table
                    # Sensor List and Legend slide

                    # rtSlide.text.text = 'Sensor measurements list: ' +str(start+ maxNofSensorMeasFirstSlide +1) +' - '+str(stop + maxNofSensorMeasFirstSlide )

                    for row in range(nofRowsRestSlides):
                        for col in range(nofColsRestSlides):
                            cell = restSlidesTablePlaceholder.cell(row, col)
                            textFrame = cell.text_frame
                            paragraph = textFrame.paragraphs[0]
                            run = paragraph.add_run()
                            if sensorMeasRestList[row, col] != '':
                                run.text = sensorMeasRestList[row, col]['dateAndTime'] + '_' + \
                                        sensorMeasRestList[row, col]['sensor']
                                # run.text = sensorMeasRestLists[slideIdx][row, col]
                            font = run.font
                            font.size = pptx.util.Pt(16)

        #List containing all the graphs with TxAnt lists
        azGraphTxAntList = []

        # List containing all the graphs with TxAnt lists
        elGraphTxAntList = []

        # Max number of TxAntennas
        maxNofTxAnt = len(txAntList)

        # Generating plot data
        if plotSetup['AzDiag'] == 1:
            #Az
            diagType = 'Az'

            for graphIdx in range(len(graphList)):
                azGraphTxAntDict = {
                    'orig': [],
                    'norm': []
                }
                # List containing all the TxAnt data per graph
                txAntPerGraphList     = []
                txAntPerNormGraphList = []

                normGraphs=0
                if plotSetup['plotOrigGraphs'] == 1:
                    normGraphs = 0
                    for txAntListIdx in range(maxNofTxAnt):
                        graphData = plt.plotTxAntDiagram(plotSetup, graphList[graphIdx], diagType, dateTimeSensorCombList, txAntList[txAntListIdx], parsedDataList, lowerMarginDict, upperMarginDict, normGraphs )
                        txAntPerGraphList.append(graphData)

                if plotSetup['plotNormGraphs'] == 1:
                    normGraphs = 1
                    for txAntListIdx in range(maxNofTxAnt):
                        graphData = plt.plotTxAntDiagram(plotSetup, graphList[graphIdx], diagType, dateTimeSensorCombList, txAntList[txAntListIdx], parsedDataList, normLowerMarginDict, normUpperMarginDict, normGraphs )
                        txAntPerNormGraphList.append(graphData)

                azGraphTxAntDict['orig'] = txAntPerGraphList
                azGraphTxAntDict['norm'] = txAntPerNormGraphList

                azGraphTxAntList.append(azGraphTxAntDict)

        if plotSetup['ElDiag'] == 1:
            # El
            diagType = 'El'
            for graphIdx in range(len(graphList)):
                elGraphTxAntDict = {
                    'orig': [],
                    'norm': []
                }
                # List containing all the TxAnt data per graph
                txAntPerGraphList = []
                txAntPerNormGraphList = []

                if plotSetup['plotOrigGraphs'] == 1:
                    normGraphs = 0
                    for txAntListIdx in range(maxNofTxAnt):
                        graphData = plt.plotTxAntDiagram(plotSetup, graphList[graphIdx], diagType, dateTimeSensorCombList, txAntList[txAntListIdx], parsedDataList, lowerMarginDict, upperMarginDict, normGraphs )
                        txAntPerGraphList.append(graphData)

                if plotSetup['plotNormGraphs'] == 1:
                    # if graphList[graphIdx]!='frequency' and graphList[graphIdx]!='time':
                    normGraphs = 1
                    for txAntListIdx in range(maxNofTxAnt):
                        graphData = plt.plotTxAntDiagram(plotSetup, graphList[graphIdx], diagType, dateTimeSensorCombList, txAntList[txAntListIdx],parsedDataList, normLowerMarginDict, normUpperMarginDict, normGraphs )
                        txAntPerNormGraphList.append(graphData)

                elGraphTxAntDict['orig'] = txAntPerGraphList
                elGraphTxAntDict['norm'] = txAntPerNormGraphList

                elGraphTxAntList.append(elGraphTxAntDict)

        # Inserting power point slides for one graph per slide configuration
        if plotSetup['graphsPerSlide'] == 1:
            #Az
            diagType='Az'
            for azGraphTxAntIdx in range(len(azGraphTxAntList)):

                azGraphTxAntDict = azGraphTxAntList[azGraphTxAntIdx]

                txAntPerGraphList = azGraphTxAntDict['orig']
                txAntPerNormGraphList = azGraphTxAntDict['norm']

                if len(txAntPerGraphList) != 0 or len(txAntPerNormGraphList) != 0:

                    nofTxAnt = len(txAntPerNormGraphList)
                    if len(txAntPerGraphList) != 0:
                        nofTxAnt = len(txAntPerGraphList)

                    for txAntGraphDataIdx in range(nofTxAnt):


                        if plotSetup['plotOrigGraphs'] == 1:
                            normGraphs = 0

                            # Adding a slide with one graph layout
                            prs.add_slide(og_layout)

                            graphData = txAntPerGraphList[txAntGraphDataIdx]

                            # Inserting slide title.
                            og_layout.title.text = plt.graphStringMapping(
                                graphData.graphTitle, normGraphs) + ' - Tx Antenna Diagrams - Type ' \
                                                  + ' - ' + dp.getAntDiagType(diagType)
                            # Inserting the description text
                            og_layout.text.text_frame.text = plt.graphStringMapping(
                                graphData.graphTitle, normGraphs) + ' - Tx Antenna Diagrams - ' \
                                                            + dp.getAntDiagType(diagType) \
                                                            + '\n' + ' - TxAnt' + str(graphData.txAnt) \
                                                            + ': CentFreq. = ' + str(
                                centFreqDictList[txAntGraphDataIdx]['avgFreqGHz']) + ' GHz (+ ' + str(
                                centFreqDictList[txAntGraphDataIdx]['posFreqDevMHz']) + ' MHz - ' + str(
                                centFreqDictList[txAntGraphDataIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                                            + 'El = ' + str(
                                normAxisAvgAngDictList[txAntGraphDataIdx][diagType]) + '\n - All sensors.'

                            imgPath = os.path.join(outputPath, graphData.figureTitle)
                            og_layout.image.insert_picture(imgPath)
                            og_layout.caption.text_frame.text = 'TxAnt' + str(graphData.txAnt)

                        ## Norm graph Slide
                        if plotSetup['plotNormGraphs'] == 1:
                            normGraphs = 1
                            graphData  = txAntPerNormGraphList[txAntGraphDataIdx]

                            if graphData.graphTitle != 'frequency' and graphData.graphTitle != 'time':
                                # Adding a slide with one graph layout
                                prs.add_slide(og_layout)
                                # Inserting slide title.
                                og_layout.title.text = plt.graphStringMapping(
                                    graphData.graphTitle,normGraphs) + ' - Tx Antenna Diagrams - Type ' \
                                                      + ' - ' + dp.getAntDiagType(diagType)
                                # Inserting the description text
                                og_layout.text.text_frame.text = plt.graphStringMapping(
                                    graphData.graphTitle,normGraphs) + ' - Tx Antenna Diagrams - ' \
                                                                + dp.getAntDiagType(diagType) \
                                                                + '\n' + ' - TxAnt' + str(graphData.txAnt) \
                                                                + ': CentFreq. = ' + str(
                                    centFreqDictList[txAntGraphDataIdx]['avgFreqGHz']) + ' GHz (+ ' + str(
                                    centFreqDictList[txAntGraphDataIdx]['posFreqDevMHz']) + ' MHz - ' + str(
                                    centFreqDictList[txAntGraphDataIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                                                + 'El = ' + str(
                                    normAxisAvgAngDictList[txAntGraphDataIdx][diagType]) + '\n - All sensors.'

                                imgPath = os.path.join(outputPath, graphData.figureTitle)
                                og_layout.image.insert_picture(imgPath)
                                og_layout.caption.text_frame.text = 'TxAnt' + str(graphData.txAnt)

            #El
            diagType = 'El'
            for elGraphTxAntIdx in range(len(elGraphTxAntList)):

                elGraphTxAntDict  = elGraphTxAntList[elGraphTxAntIdx]

                txAntPerGraphList = elGraphTxAntDict['orig']
                txAntPerNormGraphList = elGraphTxAntDict['norm']

                if len(txAntPerGraphList) != 0 or len(txAntPerNormGraphList) != 0:

                    nofTxAnt = len(txAntPerNormGraphList)

                    if len(txAntPerGraphList) != 0:
                        nofTxAnt = len(txAntPerGraphList)

                    for txAntGraphDataIdx in range(nofTxAnt):


                        if plotSetup['plotOrigGraphs'] == 1:
                            normGraphs = 0

                            # Adding a slide with one graph layout
                            prs.add_slide(og_layout)

                            graphData = txAntPerGraphList[txAntGraphDataIdx]

                            # Inserting slide title.
                            og_layout.title.text = plt.graphStringMapping(
                                graphData.graphTitle, normGraphs) + ' - Tx Antenna Diagrams - Type ' \
                                                  + ' - ' + dp.getAntDiagType(diagType)
                            # Inserting the description text
                            og_layout.text.text_frame.text = plt.graphStringMapping(
                                graphData.graphTitle, normGraphs) + ' - Tx Antenna Diagrams - ' \
                                                            + dp.getAntDiagType(diagType) \
                                                            + '\n' + ' - TxAnt' + str(graphData.txAnt) \
                                                            + ': CentFreq. = ' + str(
                                centFreqDictList[txAntGraphDataIdx]['avgFreqGHz']) + ' GHz (+ ' + str(
                                centFreqDictList[txAntGraphDataIdx]['posFreqDevMHz']) + ' MHz - ' + str(
                                centFreqDictList[txAntGraphDataIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                                            + 'El = ' + str(
                                normAxisAvgAngDictList[txAntGraphDataIdx][diagType]) + '\n - All sensors.'

                            imgPath = os.path.join(outputPath, graphData.figureTitle)
                            og_layout.image.insert_picture(imgPath)
                            og_layout.caption.text_frame.text = 'TxAnt' + str(graphData.txAnt)

                        ## Norm graph Slide
                        if plotSetup['plotNormGraphs'] == 1:
                            normGraphs = 1
                            graphData  = txAntPerNormGraphList[txAntGraphDataIdx]

                            if graphData.graphTitle != 'frequency' and graphData.graphTitle != 'time':
                                # Adding a slide with one graph layout
                                prs.add_slide(og_layout)
                                # Inserting slide title.
                                og_layout.title.text = plt.graphStringMapping(
                                    graphData.graphTitle, normGraphs) + ' - Tx Antenna Diagrams - Type ' \
                                                      + ' - ' + dp.getAntDiagType(diagType)
                                # Inserting the description text
                                og_layout.text.text_frame.text = plt.graphStringMapping(
                                    graphData.graphTitle, normGraphs) + ' - Tx Antenna Diagrams - ' \
                                                                + dp.getAntDiagType(diagType) \
                                                                + '\n' + ' - TxAnt' + str(graphData.txAnt) \
                                                                + ': CentFreq. = ' + str(
                                    centFreqDictList[txAntGraphDataIdx]['avgFreqGHz']) + ' GHz (+ ' + str(
                                    centFreqDictList[txAntGraphDataIdx]['posFreqDevMHz']) + ' MHz - ' + str(
                                    centFreqDictList[txAntGraphDataIdx]['negFreqDevMHz']) + ' MHz) , ' \
                                                                + 'El = ' + str(
                                    normAxisAvgAngDictList[txAntGraphDataIdx][diagType]) + '\n - All sensors.'

                                imgPath = os.path.join(outputPath, graphData.figureTitle)
                                og_layout.image.insert_picture(imgPath)
                                og_layout.caption.text_frame.text = 'TxAnt' + str(graphData.txAnt)

        # Inserting power point slides for two graphs per slide configuration
        elif plotSetup['graphsPerSlide'] == 2:
            #Az
            if plotSetup['AzDiag'] == 1:
                diagType = 'Az'
                dp.fillGraphSlides(prs, tg_layout, azGraphTxAntList, centFreqDictList, diagType, normAxisAvgAngDictList, plotSetup)
            # El
            if plotSetup['ElDiag'] == 1:
                diagType = 'El'
                dp.fillGraphSlides(prs, tg_layout, elGraphTxAntList, centFreqDictList, diagType, normAxisAvgAngDictList, plotSetup)

        elif plotSetup['graphsPerSlide'] == 3:
            # Az
            if plotSetup['AzDiag'] == 1:
                diagType = 'Az'
                dp.fillGraphSlides(prs, trg_layout, azGraphTxAntList, centFreqDictList, diagType, normAxisAvgAngDictList, plotSetup)
            # El
            if plotSetup['ElDiag'] == 1:
                diagType = 'El'
                dp.fillGraphSlides(prs, trg_layout, elGraphTxAntList, centFreqDictList, diagType, normAxisAvgAngDictList, plotSetup)


        elif plotSetup['graphsPerSlide'] == 4:
            # Az
            if plotSetup['AzDiag'] == 1:
                diagType = 'Az'
                dp.fillGraphSlides(prs, fg_layout, azGraphTxAntList, centFreqDictList, diagType, normAxisAvgAngDictList, plotSetup)
            # El
            if plotSetup['ElDiag'] == 1:
                diagType = 'El'
                dp.fillGraphSlides(prs, fg_layout, elGraphTxAntList, centFreqDictList, diagType, normAxisAvgAngDictList, plotSetup)

        else:
            myLogger.error('Invalig "graphPerSlide" configuration. Chose in the range: 1 - 4.')


        # Save presentation
        pathParts = os.path.split(pptxPath)
        if pathParts[1].endswith('.pptx') or pathParts[1].endswith('.ppt'):
            prs.save(pptxPath)
            # Delete extra placeholders in the presentation
            presPlace = Presentation(pptxPath)
            for slide in presPlace.slides:
                for placeholder in slide.shapes.placeholders:
                    if placeholder.has_text_frame and placeholder.text_frame.text == '':
                        rem_pc = placeholder._sp
                        rem_pc.getparent().remove(rem_pc)
            presPlace.save(pptxPath)

            if prs.saveStatus == False:
                myLogger.error(prs.saveStatusString)
            else:
                myLogger.info('PPTX file saved successfully: ' + pptxPath)
        else:
            myLogger.error('Invalid presentation file exstension. Use .pptx or .ppt')

    # Copying the LogFile to the output directory

    logFileOutputPath  = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.TxAntDiagrams.value)
    status, errorSting = aux.copyFile(log.txAntDiagLogFilePath, logFileOutputPath)
    if not status:
        myLogger.warning(errorSting)
    loadDataLogFileOutputPath = os.path.join(aux.txAntDiagOutputPath, log.LogFileNames.MainLoadData.value)
    status, errorSting = aux.copyFile(log.mainLoadDataLogFilePath, loadDataLogFileOutputPath)
    if not status:
        myLogger.warning(errorSting)


if(bUseGui):
    pass

else:
    # configuration file if the GUI is not used
    with open(os.path.join(aux.configDir, 'TxAntDiagramsConf.yaml'), 'r', encoding='utf8') as yamlfile:
        config      = yaml.safe_load(yamlfile)
        plotSetup   = config['plotSetup']
        graphConfig = config['graphConfig']
    
    txAntDiagLogger = log.txAntDiagLogger
    txAntDiagLog = log.txAntDiagLogger.logger
    errorStatus, errorSting = log.txAntDiagLogger.addFileHandler(log.txAntDiagLogFilePath, 'w+')
    if errorStatus == 1:
        txAntDiagLog.warning(errorSting)

    parseDataLogger = log.mainLoadDataLogger.logger
    parseDataLogger.info('Starting.')

    errorStatus, errorSting = log.mainLoadDataLogger.addFileHandler(log.mainLoadDataLogFilePath, 'w+')
    if errorStatus == 1:
        parseDataLogger.warning(errorSting)
    # Load Data by absolute path
    parseDataLogger.info('Loading data.')

    loadData = ld.LoadData(absPath, plotSetup['useSensorMuster'], plotSetup['sensorMusterList'])

    if loadData.invalidPath != 1:
        # myLogger.info('Num. of valid files parsed: ' + str(loadData.validFilesCounter) + '.')
        parsedDataList = loadData.parseDataList
        start_data_evaluation(parsedDataList, plotSetup, graphConfig, txAntDiagLogger, aux.txAntDiagOutputPath, 'TxAnt_Diagrams.pptx', os.path.join(aux.assetsDir, 'template.pptx'))
    else:
        parseDataLogger.error(loadData.invalidPathString)



