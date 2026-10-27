import numpy as np


def getAzPtuAngVals(txAntDiagParseData):
    angle = np.zeros(len(txAntDiagParseData.ptuPosDataList))
    for i in range(len(txAntDiagParseData.ptuPosDataList)):
        angle[i] = txAntDiagParseData.ptuPosDataList[i].d_PTU_AzAngle
    return angle

def getElPtuAngVals(txAntDiagParseData):
    angle = np.zeros(len(txAntDiagParseData.ptuPosDataList))
    for i in range(len(txAntDiagParseData.ptuPosDataList)):
        angle[i] = txAntDiagParseData.ptuPosDataList[i].d_PTU_ElAngle
    return angle

def getAzTarAngVals(txAntDiagParseData,upsideDown):
    if upsideDown == 0:
        angle = getAzPtuAngVals(txAntDiagParseData)*(-1)
    else:
        angle = getAzPtuAngVals(txAntDiagParseData)
    return angle

def getElTarAngVals(txAntDiagParseData, upsideDown):
    if upsideDown == 0:
        angle = getElPtuAngVals(txAntDiagParseData) * (-1)
    else:
        angle = getElPtuAngVals(txAntDiagParseData)
    return angle


def getLevel(txAntDiagParseData):
    level = np.zeros(getNofAngVals(txAntDiagParseData))
    for i in range(getNofAngVals(txAntDiagParseData)):
        level[i] = txAntDiagParseData.ptuPosDataList[i].level_dBm
    return level


def getLevelPowMet(txAntDiagParseData):
    level = np.zeros(getNofAngVals(txAntDiagParseData))
    for i in range(getNofAngVals(txAntDiagParseData)):
        level[i] = txAntDiagParseData.ptuPosDataList[i].levelPowMet_dBm
    return level


def getLevelMeasSpec(txAntDiagParseData):
    level = np.zeros(getNofAngVals(txAntDiagParseData))
    for i in range(getNofAngVals(txAntDiagParseData)):
        level[i] = txAntDiagParseData.ptuPosDataList[i].levelMeasSpec_dBm
    return level


def getLevelMeasPowMet(txAntDiagParseData):
    level = np.zeros(getNofAngVals(txAntDiagParseData))
    for i in range(getNofAngVals(txAntDiagParseData)):
        level[i] = txAntDiagParseData.ptuPosDataList[i].levelMeasPowMet_dBm
    return level


def getFrequency(txAntDiagParseData):
    freq = np.zeros(getNofAngVals(txAntDiagParseData))
    for i in range(getNofAngVals(txAntDiagParseData)):
        freq[i] = txAntDiagParseData.ptuPosDataList[i].frequenz_MHz
    return freq

def getTime(txAntDiagParseData):
    freq = np.zeros(getNofAngVals(txAntDiagParseData))
    for i in range(getNofAngVals(txAntDiagParseData)):
        freq[i] = txAntDiagParseData.ptuPosDataList[i].time_ms
    return freq


def getNofAngVals(ptu2ParseData):
     return len(ptu2ParseData.ptuPosDataList)

