"""Quick diagnostic: trace the Hullkurven pipeline without GUI."""
import sys, os
sys.path.insert(0, r'c:\Calibration Statistics Tool')
sys.path.insert(0, r'c:\Calibration Statistics Tool\shared')

from calibration_statistics_tool.shared import parsePTU2data as p2
from calibration_statistics_tool.shared import huellkurven_data_processing as hdp

PTU2_DIR = r'c:\Calibration Statistics Tool\measurement_data\ptu_files'

# Parse all PTU2 files
parseDataList = []
for fn in sorted(os.listdir(PTU2_DIR)):
    if fn.endswith('_ptu2.txt'):
        path = os.path.join(PTU2_DIR, fn)
        obj = p2.PTU2ParseData()
        obj.parseFile(path, 0, [])
        if obj.bDataValid:
            parseDataList.append(obj)

print(f'Parsed {len(parseDataList)} files OK\n')

chirpConfig   = {'chirp0': 1, 'chirp1': 0, 'chirp2': 0, 'chirp3': 0}
diagramConfig = {'selectDiagrams': 0, 'oddOrEven': 0, 'lowerNumber': 0, 'higherNumber': 7}
diagramConfigList = [1, 2, 3, 4]
dataConf = {'AzDiag': 1, 'ElDiag': 1, 'minSigma': -10, 'maxSigma': 10,
            'minPhaseFactor': -10, 'maxPhaseFactor': 10,
            'patternLimitsMethod': 0, 'reserveDb': 0}
inputConfig = {'diagTypeInfo': 1, 'targetAngle': 1, 'upsideDown': 0,
               'upsideDownInfo': 1, 'useSensorMuster': 0, 'sensorMusterList': []}
commentsDict = {'version': 'test'}

confChirpList    = hdp.getConfChirpList(chirpConfig)
antennaTypesList = hdp.getAntennaTypesList(parseDataList)

for antennaType in antennaTypesList:
    ptu2List = hdp.getPtu2ListPerAntennaType(antennaType, parseDataList)
    angleSetupList = hdp.setAngleSetupList(inputConfig, ptu2List)

    for angleSetup in angleSetupList:
        confPtu2List = hdp.getConfiguredPtu2Files(ptu2List, angleSetup, inputConfig)
        if not confPtu2List:
            print(f'  angleSetup={angleSetup.diagType}: confPtu2List EMPTY, skipping')
            continue

        desiredDiagramList = hdp.getDesiredDiagramsList(diagramConfig, diagramConfigList, antennaType, confPtu2List)
        centFreqDictList = []

        print(f'\nAntType{antennaType} - {angleSetup.diagType} ({len(confPtu2List)} files, {len(desiredDiagramList)} diagrams)')

        for diagListIdx in range(len(desiredDiagramList)):
            for chirp in confChirpList:
                diagNum = desiredDiagramList[diagListIdx]['diagramNum']
                avgFreq = hdp.getAvgFreqPerDiagram(chirp, diagNum, confPtu2List)
                centFreqDict = {
                    'avgFreqMHz': format(round(avgFreq / 1e6, 4), '.2f') if avgFreq else '0.00',
                    'avgFreqGHz': format(round(avgFreq / 1e9, 4), '.2f') if avgFreq else '0.00',
                    'posFreqDevMHz': '0.00',
                    'negFreqDevMHz': '0.00',
                    'diagNum': diagNum,
                    'chirp': chirp,
                }
                centFreqDictList.append(centFreqDict)

                result = hdp.createLimitsData(
                    1, commentsDict, desiredDiagramList, diagListIdx, chirp,
                    antennaType, confPtu2List, angleSetup, centFreqDictList,
                    angleSetup.diagType, inputConfig, chirpConfig, dataConf,
                    write_output=False
                )
                status = f'OK nofAntennas={result.nofAntennas}' if result else 'FAIL (no match)'
                print(f'  diagListIdx={diagListIdx} chirp={chirp} diag={diagNum} = {status}')
                if result:
                    hdp.savePlotImage(result, r'c:\Calibration Statistics Tool\output_huellkurven')

print('\nDone.')
