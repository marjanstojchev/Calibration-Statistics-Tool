import yaml
import os

import matplotlib.pyplot as plt
import numpy as np
from calibration_statistics_tool.shared import logconfig
from calibration_statistics_tool.shared import auxiliary as aux
from calibration_statistics_tool.shared import loaddata as ld
from calibration_statistics_tool.antenna_patterns import antpat_v5_data_processing as dp
import copy
import yaml


bUseGui=True

########## Configuration ###########
#absPath=r'C:\Users\Raza\Desktop\StatisticToolPython_QtGUI\PT00012245_20349KAC0KC00255_135233\2020-03-21-13-52-48_Tuner0_PT00012245_MANUAL_SN_Protocol.txt'
absPath=r'C:\Arbeit\Mobis_beispiel'
# absPath=r'\\fs9\MDSMS0\Kalibrierung\Kalibrierung_USM\Archiv\2015\2015_Typ31_STM\intern_SMS_56xT31ErstmusterZollner\UMRR-0A.49.03-00024748'
absPath=r'C:\Arbeit\noTxAnt\noDiag'
absPath = r'C:\Arbeit\noDiag_mobis'
absPath = r'C:\Arbeit\noDiag_mobis\UMRR-0A.49.03-00024748'
# absPath = r'C:\OpenAccess\von_Qi\CalData_T150ES3'
# absPath=r'C:\OpenAccess\von_Axel\Antenna_Patterns\test'
# absPath=r'C:\Arbeit\intern_8xUMRR-0A4903-1D0907fürRadarVision'
# absPath = r'\\fs9\MDSMS0\Kalibrierung\Kalibrierung_USM\Results\Typ_0x2AXAXX\2018\intern_350xUMRR-0C0304-2A2A02Nov2018'
# absPath =r'C:\Arbeit\two_antenna_types_test\rfNA_dsp0x00000007'
absPath = r'C:\Arbeit\qi_axel'
absPath = r'C:\Arbeit\ALPSsample'
absPath = r'\\ad.smartmicro.de\Data\Production\Kalibrierung\Results\Typ_0x84XXXX_UMRR-11\2019\intern_90xUMRR-110004-840101ohneLogoJuli2019'
absPath =r'\\ad.smartmicro.de\Data\Messdaten\MDSMS0\Kalibrierung\Test_TDAX_Kalibrierung\2019-11-27DevelopUmrr12T48_allWF\Messdaten'
absPath=r'C:\Hafiz\EOL_1\data'
# Script setup
setup ={
    "auto": 0, # Set 0 for manual configuration. Set 1 for automatic generation of antenna pattern tables.
    "useSensorMuster": 0,  # Set 1 to search for sensors named by specific muster, otherwise 0.for
    "sensorMusterList": []  # Sensor Muster parts list
}

# Configuration for the files WITH diaram type info.

# Chirp configuration
chirpConfig = {
    "chirp0": 1,
    "chirp1": 0,
    "chirp2": 0,
    "chirp3": 0,
}
## Header ##
antPatHeader = {

    # Name
    "type": "antennaPattern",

    # # Port identifier
    # "identifier": 36,

    # # Version
    # "majorVersion": 2,
    # "minorVersion": 0,

    # # Date
    # "year": 2020,
    # "month": 1,
    # "day": 28,

    # # Antenna information
    # "rfeGeneration": 44,
    # "rfeModification": 56,
    # "rfeRevision": 0,

}


## Data Tables ##
# "patternType": 1,     //# Antenna pattern type (0: invalid; 1: TX - RX; 2: TX; 3: RX)
# "rotationAxis": 2,    //# Antenna rotation axis (0: invalid; 1: z, azimuth; 2: y, elevation; 3: x, polarization)
# "nofApplicableTxAnt": 4,      //# [1] Number of TX antennas the pattern is applicable to
# "nofApplicableRxAnt": 4,      //# [1] Number of RX antennas the pattern is applicable to
# "applTxAntInd": [0, 0, 0, 0],     //# Indices of the TX antennas the pattern is applicable to
# "applRxAntInd": [0, 1, 2, 3],     //# Indices of the RX antennas the pattern is applicable to
# "gainCalcMethod": 1       //# [1] Method of data calculation (0: invalid, 1: step-wise, 2: interpolation )

##Port Data##
portData ={

    # Number of tables to generate
    "nofDataTables": 1,
    "version": 1
}

antPatTable0 = {
    "antenna_pattern_idx": 0,
    "patternType": 1,
    "rotationAxis": 1,
    "nofApplicableTxAnt": 1,
    "nofApplicableRxAnt": 4,
    "applTxAntInd": [0],
    "applRxAntInd": [0,1,2,3],
    "gainCalcMethod": 1
}

antPatTable1 = {
    "antenna_pattern_idx": 1,
    "patternType": 1,
    "rotationAxis": 2,
    "nofApplicableTxAnt": 1,
    "nofApplicableRxAnt": 4,
    "applTxAntInd": [0],
    "applRxAntInd": [0,1,2,3],
    "gainCalcMethod": 1
}
antPatTable2 = {
    "antenna_pattern_idx": 2,
    "patternType": 1,
    "rotationAxis": 1,
    "nofApplicableTxAnt": 2,
    "nofApplicableRxAnt": 8,
    "applTxAntInd": [0,1],
    "applRxAntInd": [0,1,2,3,4,5,6,7],
    "gainCalcMethod": 1
}
antPatTable3 = {
    "antenna_pattern_idx": 3,
    "patternType": 1,
    "rotationAxis": 2,
    "nofApplicableTxAnt": 1,
    "nofApplicableRxAnt": 8,
    "applTxAntInd": [1],
    "applRxAntInd": [0, 1,2,3,4,5,6,7],
    "gainCalcMethod": 1
}

conf0={
    "diagTypeInfo": 1, # set 1 for ptu2 files WITH diagram type info, otherwise set 0.
    "targetAngle": 1,  # Show in target angle.
    "upsideDown": 0,# Set 1 for sensor upside down, otherwise set 0.
    "upsideDownInfo": 1,  # Set 1 for ptu2 files WITH upside down info, otherwise set 0.
    "tables": [antPatTable0,antPatTable1],

}
conf1={
    "diagTypeInfo": 0, # set 1 for ptu2 files WITH diagram type info, otherwise set 0.
    "targetAngle": 1,  # Show in target angle.
    "upsideDown": 0,# Set 1 for sensor upside down, otherwise set 0.
    "upsideDownInfo": 0,  # Set 1 for ptu2 files WITH upside down info, otherwise set 0.
    "tables": [antPatTable0,antPatTable1],


}
ptu2InputConfList=[conf0]

def start_data_evaluation(parseDataList,antpatLogger):

    ########### Script ###########
    # antPatHeader = collections.OrderedDict(antPatHeader)
    # # Save as YAML
    # with open('result.yml', 'w+') as yaml_file:
    #     yaml.dump(antPatHeader, yaml_file, default_flow_style=False)


    # Maximum number of data tables allowed
    MAX_NOF_DATA_TABLES = 8

    # Output directory path
    outputPath = aux.antPatOutputPath

    # Create directory if doesn't exist
    crDirStatus, crDirErrorString = aux.createDirectory(outputPath)

    # Setup logging configuration
    myLogger = logconfig.antPatLogger.logger
    errorStatus, errorSting = logconfig.antPatLogger.addFileHandler(logconfig.antPatLogFilePath, 'w+')

    if errorStatus == 1:
        myLogger.warning(errorSting)

    if not crDirStatus:
        myLogger.error(crDirErrorString)
        return

    myLogger.info('Starting.')

    # Clear the output folder
    clearDataStatus, clearDataString = aux.clearAll(aux.antPatOutputPath)
    if not clearDataStatus:
        myLogger.error(clearDataString)
        return

    # Set number of data tables to the maximum if not satisfied
    if portData["nofDataTables"]>MAX_NOF_DATA_TABLES:
        portData["nofDataTables"]=MAX_NOF_DATA_TABLES
        myLogger.info("Nof. Data Tables adjusted to the allowed maximum: "+str(MAX_NOF_DATA_TABLES)+'.')

    ## Manual mode
    if setup["auto"]==0:

        ## Setup initialisation

        # Initialisation of the list containing the setup data for files WITH and WITHOUT diagram type info.
        confList = []
        confError=0

        for ptu2InputConfIdx in range(len(ptu2InputConfList)):

            # Initialise configured data
            ptu2InputConf=dp.Ptu2InputConf(ptu2InputConfList[ptu2InputConfIdx],ptu2InputConfIdx)
            myLogger.info("Setup for PTU2 input configuration: " + ptu2InputConf.getStr() + '.')
            configuredData=dp.Setup_v2(setup,antPatHeader,ptu2InputConf,chirpConfig,parseDataList,MAX_NOF_DATA_TABLES,portData)

            if configuredData.errorStatus==0:
                confList.append(configuredData)
            else:
                myLogger.error("Invalid PTU2 input configuration: "+ configuredData.ptu2InputConf.getStr()+'.')

        # Set error if list is empty
        if len(confList) == 0:
            confError = 1

        ## Pattern generation and plot
        # Check if the setup list error occures
        if confError == 0:
            # Traverse through the setup list
            for confIdx in range(len(confList)):

                myLogger.info("Looking for PTU2 files: " + confList[confIdx].string + ".")

                # Check if the scheduled setup is valid
                if confList[confIdx].errorStatus == 0:

                    # # Traverse through the Antenna Type list
                    # for antTypeIdx in range(len(confList[confIdx].antennaTypesList)):

                    # Traverse through the angle setup list
                    for angSetupIdx in range(len(confList[confIdx].angleSetupAzElComb)):

                        # Traverse through the chirp list
                        for chirpIdx in range(len(confList[confIdx].confChirpList)):

                            myLogger.info("Table lookup scheduled, PTU input config.: "+ confList[confIdx].ptu2InputConf.getStr() +", Antenna Type, Diagram type and Angle setup comb.: " +
                                          confList[confIdx].angleSetupAzElComb[angSetupIdx].string + ', Chirp' + str(confList[confIdx].confChirpList[chirpIdx]) + '.')

                            # Initialise YAML table data container class for each Antenna Type, Angle setup, and Chirp comb.
                            yamlTable = dp.YAML_Table()
                            yamlTable.antennaType = confList[confIdx].angleSetupAzElComb[angSetupIdx].az.antennaType
                            yamlTable.chirp = confList[confIdx].confChirpList[chirpIdx]
                            yamlTable.azElCombSetup = confList[confIdx].angleSetupAzElComb[angSetupIdx]

                            # Traverse through the configured tables list
                            for tabIdx in range(len(confList[confIdx].confTablesList)):

                                myLogger.info("Lookig for data: " + confList[confIdx].ptu2InputConf.getStr()+", Antenna Type, Diagram type and Angle setup comb.: " +
                                              confList[confIdx].angleSetupAzElComb[angSetupIdx].string + ' - Chirp' + str(confList[confIdx].confChirpList[chirpIdx]) + \
                                              ' - Table' + str(confList[confIdx].confTablesList[tabIdx].antennaPatternIdx) + ' - ' +confList[confIdx].confTablesList[tabIdx].getStr())


                                if confList[confIdx].confTablesList[tabIdx].rotationAxis == 1:
                                    dataTable = dp.DataTable(
                                        confList[confIdx].angleSetupAzElComb[angSetupIdx].az,
                                        confList[confIdx].confTablesList[tabIdx],
                                        confList[confIdx].confChirpList[chirpIdx], parseDataList,
                                        confList[confIdx].ptu2InputConf)
                                else:
                                    dataTable = dp.DataTable(
                                        confList[confIdx].angleSetupAzElComb[angSetupIdx].el,
                                        confList[confIdx].confTablesList[tabIdx],
                                        confList[confIdx].confChirpList[chirpIdx], parseDataList,
                                        confList[confIdx].ptu2InputConf)


                                ## Plot initialisation ##
                                #  Close all the figure windows
                                plt.close("all")

                                # Create subplots and plot figure
                                fig, ax1 = plt.subplots()

                                # Invert axis for showing angle from right to left
                                plt.gca().invert_xaxis()

                                # Show plot grid
                                plt.grid(True)

                                # Set title to the graph figure
                                ax1.set_title("Antenna Patterns")

                                # Set y-axis label for specific general graph types
                                ax1.set_ylabel("Norm. Level [dB]")

                                # Set the x-axis label
                                ax1.set_xlabel('PTU Angle [°]')

                                # Streching the x axis data from end to end
                                ax1.autoscale(enable=True, axis='x', tight=True)

                                # Set plot x-axis label.
                                if confList[confIdx].ptu2InputConf.targetAngle == 1:
                                    ax1.set_xlabel('Target Angle [°]')

                                # Check if the Data Table object contains data for the input parameters.
                                if dataTable.errorStatus == 0:

                                    # Initialise the parameters for the angle and the average normalised level
                                    nofParsedFiles = len(dataTable.tableMeasDataList)
                                    angle = dataTable.angle
                                    avgNormLevelPerFileSumW = 0
                                    avgNormLevelW = 0

                                    # Traverse through each parsed PTU2 data cntained at the data table.
                                    for parFileIdx in range(nofParsedFiles):
                                        # Traverse through the configured Rx antennas.
                                        for rxAntIdx in range(len(dataTable.tableMeasDataList[parFileIdx].normLevelList)):
                                            # Get and plot the normalised level dB values for each Rx antenna.
                                            normLevelRxAntDb = \
                                            dataTable.tableMeasDataList[parFileIdx].normLevelList[rxAntIdx]
                                            ax1.plot(angle, normLevelRxAntDb, '.-')

                                        # Get the average normalised level from each Rx antenna, per PTU2 file.
                                        avgNormLevelPerFileW = dataTable.tableMeasDataList[
                                            parFileIdx].rxAntAvgNormLevelW
                                        avgNormLevelPerFileDb = dataTable.tableMeasDataList[
                                            parFileIdx].rxAntAvgNormLevelDb

                                        # Sum the average normalised level of eash PTU2 file for the purpose of calculating the average of it.
                                        avgNormLevelPerFileSumW = avgNormLevelPerFileSumW + avgNormLevelPerFileW

                                    # Average of the normalised level averages from each PTU2 file.
                                    avgNormLevelW = avgNormLevelPerFileSumW / nofParsedFiles

                                    # Convert the average norm level of all PTU2 files in dB, plot, and save figure.
                                    avgNormLevelDb = 10 * np.log10(avgNormLevelW)
                                    dataTable.avgNormLevelDb = avgNormLevelDb
                                    lines = ax1.plot(angle, avgNormLevelDb)
                                    plt.setp(lines, linestyle='--', linewidth='4', color='gold')
                                    figureTitle = dataTable.getStr()
                                    ax1.set_title(figureTitle)

                                    figurePath = os.path.join(outputPath, figureTitle)
                                    saveFig, saveFigStr = aux.saveFig(fig, figurePath)
                                    if saveFig:
                                        myLogger.info("Image generated: " + figureTitle)
                                    else:
                                        myLogger.warning(saveFigStr)

                                    # Append the table to the data table list in the YAML_Table object.
                                    validDataTable = copy.deepcopy(dataTable)
                                    yamlTable.dataTablesList.append(validDataTable)

                                else:
                                    # Data table doesnt contain data for the certain input parameters.
                                    myLogger.error("No available data for the scheduled Table found.\n")
                                    # Close the empty figure, otherwise it opens as a blank window on the next plt.show().
                                    plt.close(fig)

                            # Append the the YAML_Table to the YAML tables list in the Setup object.
                            confList[confIdx].yamlTablesList.append(yamlTable)
                else:
                    # No data for the certain Setup found.
                    myLogger.error("No data for setup " + confList[confIdx].string + " found")

        else:
            # Incorrect configuration.
            myLogger.error("Incorrect configuration.")

    ## YAML Table generation

    # Check if configuration is correct.
    if confError==0:
        # Traverse through the setup list.
        for confIdx in range(len(confList)):

            myLogger.info("Looking for YAML tables data for setup " +confList[confIdx].string+ '.')

            # Check if the setup list is not empty.
            if confList[confIdx].errorStatus == 0:

                # # Traverse through the Antenna Type list.
                # for antTypeIdx in range(len(confList[confIdx].antennaTypesList)):

                # Traverse through the angle setup list.
                for angSetupIdx in range(len(confList[confIdx].angleSetupAzElComb)):

                    # Traverse through the chirp list.
                    for chirpIdx in range(len(confList[confIdx].confChirpList)):

                        # Check if the YAML_Table list for certain Setup is not empty.
                        if len(confList[confIdx].yamlTablesList)!=0:

                           # Traverse through the YAML_Table list.
                            for yamlTableIdx in range(len(confList[confIdx].yamlTablesList)):

                                # Check if the actual YAML_Table matches for the iteration with certain Antenna Type, Angle setup, and Chirp.
                                if confList[confIdx].yamlTablesList[yamlTableIdx].chirp==confList[confIdx].confChirpList[chirpIdx] and confList[confIdx].yamlTablesList[yamlTableIdx].azElCombSetup ==confList[confIdx].angleSetupAzElComb[angSetupIdx]:

                                    myLogger.info("Generating YAML file: "+confList[confIdx].string +", Antenna Type, Diagram type and Angle setup comb.: " + confList[confIdx].angleSetupAzElComb[angSetupIdx].string + ', Chirp' + str(confList[confIdx].confChirpList[chirpIdx]) + '.')

                                    # Assign JSOn file title and reorder data tables list which contains only valid data tables.
                                    yamlFileTitle =confList[confIdx].string +' - '+confList[confIdx].angleSetupAzElComb[angSetupIdx].string + ' - ' + 'Chirp' + str(confList[confIdx].confChirpList[chirpIdx]) + '.yaml'

                                    yamlTable=confList[confIdx].yamlTablesList[yamlTableIdx]
                                    yamlTable.reorderDataTablesList()
                                    yamlTable.yamlFileTitle = yamlFileTitle

                                    # Assign the Antenna Patterns header to the YAML_Table object and adjust the nof. data tables and rfeGeneration.
                                    outputDict = copy.deepcopy(confList[confIdx].antPatHeader)
                                    portData1 =copy.deepcopy(confList[confIdx].portData)
                                    portData1["nofDataTables"] = len(yamlTable.dataTablesList)
                                    outputDict["rfeGeneration"]=confList[confIdx].yamlTablesList[yamlTableIdx].antennaType
                                    yamlTable.outputDict = outputDict
                                    yamlTable.portData = portData1

                                    myLogger.info("Nof. data tables adjusted to the number of available data tables: " + str(yamlTable.portData["nofDataTables"]) + '.')

                                    # Check if the YAML_Table contains data tables
                                    if len(yamlTable.dataTablesList)!=0:

                                        # Traverse through the data tables list
                                        for dataTableIdx in range(len(yamlTable.dataTablesList)):

                                            # Reorder angle and avg normalised level data for the purpose of presenatation.
                                            dataTable=yamlTable.dataTablesList[dataTableIdx]

                                            upsideDown=dp.getUpsideDown(dataTable.tableMeasDataList[0].parseData, dataTable.ptu2InputConf)
                                            angleData=dataTable.angle
                                            normLevelData = dataTable.avgNormLevelDb
                                            # revOrderAngle = angleData[::-1]
                                            if dataTable.ptu2InputConf.targetAngle==1 and upsideDown==0:
                                                angleData=angleData[::-1]
                                                normLevelData = normLevelData[::-1]

                                            angleData=angleData.tolist()
                                            # revOrderAngle = revOrderAngle.tolist()

                                            normLevelData = normLevelData.tolist()
                                            # revOrderNormLevel = normLevelData[::-1]
                                            # revOrderNormLevel = revOrderNormLevel.tolist()

                                            # Append the data tables dict to the list.
                                            yamlTable.dataTablesDictList.append({

                                                #"antenna_pattern_idx": dataTable.configTable.antennaPatternIdx,
                                                "patternType": dataTable.configTable.patternType,
                                                "rotationAxis": dataTable.configTable.rotationAxis,
                                                #"nofApplicableTxAnt": dataTable.configTable.nofApplicableTxAnt,
                                                #"nofApplicableRxAnt": dataTable.configTable.nofApplicableRxAnt,
                                                "applTxAntIdx":{"start": dataTable.configTable.applTxAntInd},
                                                "applRxAntIdx":{"start": dataTable.configTable.applRxAntInd},
                                                #"gainCalcMethod": dataTable.configTable.gainCalcMethod,
                                                #"nofAngleValues": dataTable.nofAngleValues,
                                                "angle":{"start": angleData},
                                                "normGainDb":{"start": normLevelData}
                                            })

                                        #create meta dict
                                        yamlTable.outputDict.update({"meta" : 
                                                                    { "version":1,
                                                                    "housingGeneration": 7,
                                                                    "housingModification": 7,
                                                                    "rfeGeneration": confList[confIdx].yamlTablesList[yamlTableIdx].antennaType,
                                                                    "rfeModification": 0,
                                                                    "source": "measurement"}})

                                        # Form a dict of the data tables
                                        dataTablesDict = {"patterns":{"start": yamlTable.dataTablesDictList}}

                                        # Update port data with data tables
                                        portData1.update(dataTablesDict)

                                        # Form a dict of the data tables
                                        portDataDict = {"data": portData1}

                                        # Assemble the header part with the port data.
                                        yamlTable.outputDict.update(portDataDict)
                                        

                                        outputPath = os.path.join(aux.antPatOutputPath, yamlTable.yamlFileTitle)

                                        # myLogger.info('YAML file generated: ' + yamlTable.yamlFileTitle + '.')

                                        # Save as YAML
                                        yamlComment = "#patternType - Antenna pattern type (0: invalid; 1: TX - RX; 2: TX; 3: RX).\n" + \
                                                      "#rotationAxis - Antenna rotation axis (0: invalid; 1: z, azimuth; 2: y, elevation).\n" + \
                                                      "#applTxAntIdx - [1] Indices of the TX antennas the pattern is applicable to.\n" + \
                                                      "#applRxAntIdx - [1] Indices of the RX antennas the pattern is applicable to.\n" + \
                                                      "#angle - [deg] Antenna pattern angle values.\n" + \
                                                      "#normGainDb - [dB] Normalized antenna pattern gain values.\n"
                                                      #"#antenna_pattern_idx - Index of the data table.\n" + \
                                                      #"#nofApplicableTxAnt - [1] Number of TX antennas the pattern is applicable to.\n" + \
                                                      #"#nofApplicableRxAnt - [1] Number of RX antennas the pattern is applicable to.\n" + \
                                                      #"#gainCalcMethod - Method of data calculation (0: invalid, 1: step-wise, 2: interpolation).\n" + \
                                                      #"#nofAngleValues - [1] Number of angle values.\n" + \

                                        with open(outputPath, 'w+') as yaml_file:
                                            yaml_file.write(yamlComment)
                                            yaml.dump(yamlTable.outputDict, yaml_file, default_flow_style=False,sort_keys=False)

                                    else:
                                        # No data tables found for the certain configuration
                                        myLogger.error('No data tables for YAML file found, Antenna Type: '+str(confList[confIdx].yamlTablesList[yamlTableIdx].antennaType) +', Diagram type and Angle setup comb.: '+confList[confIdx].angleSetupAzElComb[angSetupIdx].string + ', Chirp' + str(confList[confIdx].confChirpList[chirpIdx]) + '.')

                        else:
                            # No YAML tables found for the certain Setup.
                            myLogger.error("No YAML tables for setup " + confList[confIdx].string + ' available.')
    #

    # Copying the LogFile to the output directory
    logFileOutputPath = os.path.join(aux.antPatOutputPath, logconfig.LogFileNames.AntennaPatterns.value)
    status, errorSting =aux.copyFile(logconfig.antPatLogFilePath, logFileOutputPath)
    if not status:
        myLogger.warning(errorSting)

    loadDataLogFileOutputPath = os.path.join(aux.antPatOutputPath, logconfig.LogFileNames.MainLoadData.value)
    status,errorSting = aux.copyFile(logconfig.antPatLogFilePath, loadDataLogFileOutputPath)
    if not status:
        myLogger.warning(errorSting)
        
if(bUseGui):
    pass

else:

    # import antpat_logconfig
    antpatLogger = logconfig.antPatLogger
    antpatLog = logconfig.antPatLogger.logger
    errorStatus, errorSting = logconfig.antPatLogger.addFileHandler(logconfig.antPatLogFilePath, 'w+')

    if errorStatus ==1:
        antpatLog.warning(errorSting)
    antpatLog.info('Starting.')
    # Load Data by absolute path
    antpatLog.info('Loading data.')
    loadData = ld.LoadData(absPath,setup["useSensorMuster"],setup["sensorMusterList"])

    if loadData.invalidPath != 1:
        # myLogger.info("Num. of valid files parsed: " + str(loadData.validFilesCounter) + ".")
        parseDataList = loadData.parseDataList
        start_data_evaluation(parseDataList,antpatLogger)
    else:
        antpatLog.error(loadData.invalidPathString)
