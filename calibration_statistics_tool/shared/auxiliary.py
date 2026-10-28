from __future__ import annotations
import os
import shutil
from shutil import copyfile
import errno
from calibration_statistics_tool.shared import logconfig
from calibration_statistics_tool.shared import user_paths as _up
import enum

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

# Output base comes from <home>/paths.json (default home: ~/Documents/calibration-tool,
# see user_paths).  On first run the file is created automatically.
# Edit it to change the output location.
_outputBase = _up.output_base
basicDir = _outputBase  # backward-compat alias

# Config base: resolve from this file's location so the bundled config/
# directory is found both in the source tree and after pip install.
_configBase = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Expose the user paths config file so the GUI can show/edit it.
userPathsFile = _up.PATHS_FILE

# Input directory defaults (set in paths.json; empty string = OS default).
inputProtocolDir: str = _up.input_protocol_dir
inputPtuDir: str = _up.input_ptu_dir
inputTxAntDir: str = _up.input_tx_ant_dir

# Output paths
antSysDiagOutputPath = os.path.join(_outputBase, OutputFolderNames.AntennaSystemDiagrams.value)
antPatOutputPath = os.path.join(_outputBase, OutputFolderNames.AntennaPatterns.value)
huellKurvenOutputPath = os.path.join(_outputBase, OutputFolderNames.HuellKurven.value)
txAntDiagOutputPath = os.path.join(_outputBase, OutputFolderNames.TxAntDiagrams.value)
setCurvesOutputPath = os.path.join(_outputBase, OutputFolderNames.SetCurves.value)
# mainLoadDataOutputPath = os.path.join(_outputBase, OutputFolderNames.LoadData.value)
certificatesOutputPath = os.path.join(_outputBase, OutputFolderNames.Certificates.value)
statisticOutputPath = os.path.join(_outputBase, OutputFolderNames.Statistic.value)
mergeOutputPath = os.path.join(_outputBase, OutputFolderNames.merge.value)

#setcurves
setcurvesinputconffilename = 'SetCurvesInputConf.json'
setcurvesinputconffilepath = os.path.join(_outputBase, setcurvesinputconffilename)
setcurvescustinputconffilename = 'SetCurvesCustomerInputConf.json'
setcurvescustinputconffilepath = os.path.join(_outputBase, setcurvescustinputconffilename)

# Config files (limits YAML + stats JSON) and asset templates (PPTX) are
# seeded to <home>/config and <home>/templates on first run by
# user_paths._copy_defaults_if_missing().  Users can edit them and upgrades
# won't overwrite.
configDir = _up.config_dir

assetsDir = _up.templates_dir

#stats input config
statsinputconffilename = 'StatisticsLimitsConfig.json'
statsinputconffilepath = os.path.join(configDir, statsinputconffilename)

burnInLimitsFileName = 'BurnInLimits.yaml'
burnInLimitsFilePath = os.path.join(configDir, burnInLimitsFileName)

calLimitsFileName = 'CalLimits.yaml'
calLimitsFilePath = os.path.join(configDir, calLimitsFileName)

burnInLimGroupsFileName = 'BurnInLimGroups.yaml'
burnInLimGroupsFilePath = os.path.join(configDir, burnInLimGroupsFileName)

calLimGroupsFileName = 'CalLimGroups.yaml'
calLimGroupsFilePath = os.path.join(configDir, calLimGroupsFileName)

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
