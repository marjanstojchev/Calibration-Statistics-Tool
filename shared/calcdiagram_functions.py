import numpy as np

LIGHT_SPEED=299792458.0

def getAvgAntLevel(rxAnt,ptu2ParseData):
    nofActiveChirps=0
    avgData=np.zeros(getNofAngVals(ptu2ParseData))
    for chirp in range(ptu2ParseData.MAX_CHIRP):
        if ptu2ParseData.chirpInfoList[chirp].active==1:
            nofActiveChirps+=1
            currData = getAntLevel(rxAnt, chirp, ptu2ParseData)
            avgData += 10 ** (currData / 10)  # accumulate in Watts
    avgData=avgData/nofActiveChirps
    avgData=10 * np.log10(avgData)
    return avgData

def getAvgNormAntLevel(rxAnt,ptu2ParseData):
    nofActiveChirps=0
    avgData=np.zeros(getNofAngVals(ptu2ParseData))
    for chirp in range(ptu2ParseData.MAX_CHIRP):
        if ptu2ParseData.chirpInfoList[chirp].active==1:
            nofActiveChirps+=1
            currData = getNormAntLevel(rxAnt, chirp, ptu2ParseData)
            avgData += 10 ** (currData / 10)  # accumulate in Watts
    avgData=avgData/nofActiveChirps
    avgData=10 * np.log10(avgData)
    return avgData

# def toTargetAngle(ptu2ParseData):
#     for i in range(len(ptu2ParseData.ptuPosDataList)):
#         ptu2ParseData.ptuPosDataList[i].d_PTU_Angle *=-1
#     return ptu2ParseData

def getPtuAngVals(ptu2ParseData):
    if ptu2ParseData.angles_array is not None:
        return ptu2ParseData.angles_array
    return np.array([pos.d_PTU_Angle for pos in ptu2ParseData.ptuPosDataList], dtype=np.float64)

def getTarAngVals(ptu2ParseData,upsideDown):
    if upsideDown==0:
        angle= getPtuAngVals(ptu2ParseData)*(-1)
    else:
        angle =getPtuAngVals(ptu2ParseData)
    return angle

def getAntLevel(rxAnt,chirp,ptu2ParseData):
    if ptu2ParseData.levels_array is not None:
        return ptu2ParseData.levels_array[:, chirp, rxAnt].copy()
    return np.array([pos.chirpMeasDataList[chirp].antennaLevelDataList[rxAnt].dLevel
                     for pos in ptu2ParseData.ptuPosDataList], dtype=np.float64)

def getNormAntLevel(rxAnt,chirp,ptu2ParseData):
    normLevel=getAntLevel(rxAnt,chirp,ptu2ParseData)
    normLevel=normLevel - np.max(normLevel)
    return normLevel

def getNofAngVals(ptu2ParseData):
     return len(ptu2ParseData.ptuPosDataList)

def getPhaseDiff(phaseDiffIdx, chirp, ptu2ParseData):
    if ptu2ParseData.phases_array is not None:
        return ptu2ParseData.phases_array[:, chirp, phaseDiffIdx].copy()
    return np.array([pos.chirpMeasDataList[chirp].diffPhaseDataList[phaseDiffIdx].dDiffPhase
                     for pos in ptu2ParseData.ptuPosDataList], dtype=np.float64)

def getAvgPhaseDiff(phaseDiffIdx, ptu2ParseData):
    nofActiveChirps=0
    avgData=np.zeros(getNofAngVals(ptu2ParseData))
    for chirp in range(ptu2ParseData.MAX_CHIRP):
        # currData = getPhaseDiff(phaseDiffIdx, chirp, ptu2ParseData)
        currData = getPhaseDiffOffCorr(phaseDiffIdx, chirp, ptu2ParseData)
        if ptu2ParseData.chirpInfoList[chirp].active==1:
            nofActiveChirps+=1
            avgData=avgData + currData
    avgData=avgData/nofActiveChirps
    return avgData

def getAvgPhaseDiffDiff(phaseDiffIdx, ptu2ParseData):
    nofActiveChirps=0
    avgData=np.zeros(getNofAngVals(ptu2ParseData))
    for chirp in range(ptu2ParseData.MAX_CHIRP):
        currData = getPhaseDiffDiff(phaseDiffIdx, chirp, ptu2ParseData)
        if ptu2ParseData.chirpInfoList[chirp].active==1:
            nofActiveChirps+=1
            avgData=avgData + currData
    avgData=avgData/nofActiveChirps
    return avgData

def getIdealPhaseDiff(phaseDiffIdx, chirp, ptu2ParseData):
    angle=getPtuAngVals(ptu2ParseData)
    # angle=np.arange(-90,91)
    angle=angle*(-1)
    antDistance =ptu2ParseData.antennaInfo.antennaDistancesList[phaseDiffIdx]
    centerFrequency=ptu2ParseData.chirpInfoList[chirp].centerFrequency
    idealPhaseDiff =((np.sin(angle / 180.0 * np.pi) * 360.0 * antDistance * centerFrequency) / LIGHT_SPEED)
    idealPhaseDiff=getPhaseInRange(idealPhaseDiff)
    return idealPhaseDiff

def getPhaseDiffDiff(phaseDiffIdx, chirp, ptu2ParseData):
    # phaseDiff=getPhaseDiff(phaseDiffIdx, chirp, ptu2ParseData)
    phaseDiffOffCorr = getPhaseDiffOffCorr(phaseDiffIdx, chirp, ptu2ParseData)
    idealPhaseDiff=getIdealPhaseDiff(phaseDiffIdx, chirp, ptu2ParseData)
    diff=phaseDiffOffCorr-idealPhaseDiff
    diff=getPhaseInRange(diff)
    return diff

def getPhaseDiffOffCorr(phaseDiffIdx, chirp, ptu2ParseData):
    phaseDiff = getPhaseDiff(phaseDiffIdx, chirp, ptu2ParseData)
    offset = ptu2ParseData.chirpInfoList[chirp].diffPhaseOffsetList[phaseDiffIdx]
    offsetCorr = phaseDiff + offset
    offsetCorr=getPhaseInRange(offsetCorr)
    return offsetCorr

# replace the 180° jumps with continious data, PTU angle regarded
def getPhaseDiffOffCorrCont(phaseDiffIdx, chirp, ptu2ParseData):
    phaseDiffCorr=getPhaseDiffOffCorr(phaseDiffIdx, chirp, ptu2ParseData)

    # x=copy.copy(phaseDiffCorr)
    zeroDegIdxOdd=0
    zeroDegIdxUpper=0
    zeroDegIdxLower=0

    medianDifference=0

    tolerance=0
    HALF_TURN=180
    WHOLE_TURN=360

    if len(phaseDiffCorr) % 2 ==0:
        zeroDegIdxLower =int(len(phaseDiffCorr) / 2) -1
        zeroDegIdxUpper =int(len(phaseDiffCorr)/2)

    else:
        zeroDegIdxOdd = int((len(phaseDiffCorr) - 1) / 2)
        zeroDegIdxLower = zeroDegIdxUpper =  zeroDegIdxOdd

    diff=0
    incr=0
    # valst=phaseDiffCorr[145]
    # phaseDiffCorr[145::]=valst
    # phaseDiffCorr[158] = 0
    # phaseDiffCorr[159]=50
    # phaseDiffCorr[160] =-50
    outputArray=np.zeros(len(phaseDiffCorr))
    for idx in range(zeroDegIdxUpper,len(phaseDiffCorr)):
        current=phaseDiffCorr[idx]
        previous=phaseDiffCorr[idx - 1]
        diff=(phaseDiffCorr[idx] - phaseDiffCorr[idx - 1])
        if (diff > HALF_TURN):
            incr -= WHOLE_TURN

        if diff < (-1*HALF_TURN):
            incr += WHOLE_TURN

        outputArray[idx] = phaseDiffCorr[idx] + incr

    diff = 0
    incr = 0
    for idx in range(zeroDegIdxLower, -1, -1):
        current = phaseDiffCorr[idx]
        previous = phaseDiffCorr[idx + 1]
        diff = (phaseDiffCorr[idx] - phaseDiffCorr[idx + 1])
        if (diff > HALF_TURN):
            incr -= WHOLE_TURN

        if diff < (-1 * HALF_TURN):
            incr += WHOLE_TURN

        outputArray[idx] = phaseDiffCorr[idx] + incr

    return outputArray

    #             posJump = True
    #             lowerPartJumpIndices.append(idx)
    #
    #     # neg jump
    #     elif negJumpRange[0] <= (phaseDiffCorr[idx] - phaseDiffCorr[idx + 1]) <= negJumpRange[1]:
    #         if not posJump:
    #             negJump = True
    #             lowerPartJumpIndices.append(idx)
    #
    # lowerPartJumpIndices.append(lastIdx)
    #
    # if posJump:
    #     for idxOfIdx in range(len(lowerPartJumpIndices)):
    #
    #         if idxOfIdx !=0:
    #             endIdx = lowerPartJumpIndices[idxOfIdx]
    #             startIdx = lowerPartJumpIndices[idxOfIdx - 1]
    #             rev = idxOfIdx - 1
    #
    #             if idxOfIdx!= len(lowerPartJumpIndices)-1:
    #
    #                 phaseDiffCorr[startIdx:endIdx:-1] = [value - rev * WHOLE_TURN for value in phaseDiffCorr[startIdx:endIdx:-1]]
    #             else:
    #
    #                 phaseDiffCorr[startIdx::-1] = [value - rev * WHOLE_TURN for value in phaseDiffCorr[startIdx::-1]]
    #
    # elif negJump:
    #
    #     for idxOfIdx in range(len(lowerPartJumpIndices)):
    #
    #         if idxOfIdx !=0:
    #             endIdx = lowerPartJumpIndices[idxOfIdx]
    #             startIdx = lowerPartJumpIndices[idxOfIdx - 1]
    #             rev = idxOfIdx - 1
    #
    #             if idxOfIdx!= len(lowerPartJumpIndices)-1:
    #
    #                 phaseDiffCorr[startIdx:endIdx:-1] = [value + rev * WHOLE_TURN for value in phaseDiffCorr[startIdx:endIdx:-1]]
    #
    #                 # temp1 = phaseDiffCorr[startIdx:endIdx:-1] = [value - rev * WHOLE_TURN for value in
    #                 #                                              phaseDiffCorr[startIdx:endIdx:-1]]
    #                 # temp.append(temp1)
    #                 # tempI1 = idice[startIdx:endIdx:-1] = [i for i in idice[startIdx:endIdx:-1]]
    #                 # tempI.append(tempI1)
    #             else:
    #
    #                 phaseDiffCorr[startIdx::-1] = [value + rev * WHOLE_TURN for value in phaseDiffCorr[startIdx::-1]]
    #
    #                 # temp1 = phaseDiffCorr[startIdx::-1] = [value - rev * WHOLE_TURN for value in
    #                 #                                              phaseDiffCorr[startIdx::-1]]
    #                 # temp.append(temp1)
    #                 # tempI1 = idice[startIdx::-1] = [i for i in idice[startIdx::-1]]
    #                 # tempI.append(tempI1)
    #
    #
    # return phaseDiffCorr

def getPhaseInRange(graphArray):
    graphArray = np.where(graphArray >  180, graphArray - 360, graphArray)
    graphArray = np.where(graphArray < -180, graphArray + 360, graphArray)
    return graphArray
