import ctypes

vol = (ctypes.windll.winmm.waveOutGetVolume)
print(vol)