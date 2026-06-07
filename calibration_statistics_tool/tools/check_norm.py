import numpy as np
from calibration_statistics_tool.shared.parsePTU2data import PTU2ParseData, parseFile
from calibration_statistics_tool.shared import calcdiagram_functions as calc

f1 = 'measurement_data/ptu_files/2024-01-15_11-45-30_Tuner1_rf12345_dsp67890_Seq1_TxAnt2_Diagram4_Az_ptu2.txt'
f2 = 'measurement_data/ptu_files/2024-01-15_11-45-30_Tuner1_rf12346_dsp67891_Seq1_TxAnt2_Diagram4_Az_ptu2.txt'

p1 = PTU2ParseData()
parseFile(f1, p1)

p2 = PTU2ParseData()
parseFile(f2, p2)

# choose chirp 0 and rxAnt 0 (adjust if needed)
chirp = 0
rxAnt = 0

raw1 = calc.getAntLevel(rxAnt, chirp, p1)
raw2 = calc.getAntLevel(rxAnt, chirp, p2)

norm1 = calc.getNormAntLevel(rxAnt, chirp, p1)
norm2 = calc.getNormAntLevel(rxAnt, chirp, p2)

print('file1:', f1)
print('file2:', f2)
print('raw shapes:', raw1.shape, raw2.shape)
print('raw maxes:', np.max(raw1), np.max(raw2))
print('raw allclose:', np.allclose(raw1, raw2))
print('raw max abs diff:', np.max(np.abs(raw1 - raw2)))
print('norm allclose:', np.allclose(norm1, norm2))
print('norm max abs diff:', np.max(np.abs(norm1 - norm2)))
print('first 5 raw1:', raw1[:5])
print('first 5 raw2:', raw2[:5])
print('first 5 norm1:', norm1[:5])
print('first 5 norm2:', norm2[:5])
