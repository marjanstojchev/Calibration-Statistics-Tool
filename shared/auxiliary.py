from __future__ import annotations
import os
import shutil
from shutil import copyfile
import errno
import logconfig
import enum
import sys

class OutputFolderNames(enum.Enum):
    AntennaSystemDiagrams='output'
    TxAntDiagrams='output_tx_diagrams'
    AntennaPatterns='output_antenna_patterns'
    HuellKurven = 'output_huellkurven'
    Certificates='output_certificates'
    SetCurves='output_setcurves'
    Statistic='output_statistic'
    merge= 'output_merge'


# Get logger
myLogger=logconfig.mainLoadDataLogger.logger

# Basic directory
# basicDir = os.path.dirname(os.path.abspath(__file__))
basicDir = os.path.dirname(sys.argv[0])

# Output pazh
antSysDiagOutputPath = os.path.join(basicDir, OutputFolderNames.AntennaSystemDiagrams.value)
antPatOutputPath = os.path.join(basicDir, OutputFolderNames.AntennaPatterns.value)
huellKurvenOutputPath = os.path.join(basicDir, OutputFolderNames.HuellKurven.value)
txAntDiagOutputPath = os.path.join(basicDir, OutputFolderNames.TxAntDiagrams.value)
setCurvesOutputPath = os.path.join(basicDir, OutputFolderNames.SetCurves.value)
# mainLoadDataOutputPath = os.path.join(basicDir, OutputFolderNames.LoadData.value)
certificatesOutputPath = os.path.join(basicDir, OutputFolderNames.Certificates.value)
statisticOutputPath = os.path.join(basicDir, OutputFolderNames.Statistic.value)
mergeOutputPath = os.path.join(basicDir, OutputFolderNames.merge.value)

#setcurves
setcurvesinputconffilename = 'SetCurvesInputConf.json'
setcurvesinputconffilepath = os.path.join(basicDir, setcurvesinputconffilename)
setcurvescustinputconffilename = 'SetCurvesCustomerInputConf.json'
setcurvescustinputconffilepath = os.path.join(basicDir, setcurvescustinputconffilename)

#stats input config
statsinputconffilename = 'StatisticsLimitsConfig.json'
statsinputconffilepath = os.path.join(basicDir, statsinputconffilename)

burnInLimitsFileName = 'BurnInLimits.yaml'
burnInLimitsFilePath = os.path.join(basicDir, burnInLimitsFileName)

calLimitsFileName = 'CalLimits.yaml'
calLimitsFilePath = os.path.join(basicDir, calLimitsFileName)

burnInLimGroupsFileName = 'BurnInLimGroups.yaml'
burnInLimGroupsFilePath = os.path.join(basicDir, burnInLimGroupsFileName)

calLimGroupsFileName = 'CalLimGroups.yaml'
calLimGroupsFilePath = os.path.join(basicDir, calLimGroupsFileName)

# Clear the output directory
def clearAll(outputFolderPath: str) -> tuple[bool, str]:
    status = True
    errorString = 'Clearing output directory: Status OK.'
    try:
        for the_file in os.listdir(outputFolderPath):
            file_path = os.path.join(outputFolderPath, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                errorString = "Clearing output directory: " + str(e)
                status=False
    except Exception as e:
        errorString = "Clearing output directory: " + str(e)
    return status,errorString

def createDirectory(outputPath: str) -> tuple[bool, str]:
    errorStr = 'Creating directory OK, path: '+ outputPath +'.'
    status=True
    if not os.path.isdir(outputPath):
        try:
            os.makedirs(outputPath)
            # myLogger.info(errorStr)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                errorStr = str(exc.errno)
                status=False
                # myLogger.error(errorStr)
    return status, errorStr

def copyFile(src: str, dest: str) -> tuple[bool, str]:
    errorStr='Copying: Status OK.'
    status = True
    try:
        copyfile(src,dest)
    except Exception as e:
        errorStr='Copying: '+str(e)
        status=False

    return status,errorStr

# Save the plotted graph figure with a given title.
def saveFig(fig, figurePath: str) -> tuple[bool, str]:
    status=True
    errorStr=''
    figurePath=figurePath+'.png'
    fig.set_figheight(9)
    fig.set_figwidth(16)
    figurePath=os.path.join(figurePath,figurePath)
    try:
        fig.savefig(figurePath, dpi=150)
    except Exception as e:
        errorStr='Saving figure: '+str(e)
        status=False
    return status, errorStr
