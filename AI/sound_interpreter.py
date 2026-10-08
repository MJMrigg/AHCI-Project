import numpy as np
import sounddevice as sd

SR = 32000 # samples per sec

print("Listening...")
while True:
    audio = sd.rec(SR, samplerate=SR, channels=1, dtype="float32")
    sd.wait()
    audio = audio[:, 0]

    loudness = np.sqrt(np.mean(audio ** 2))
    if loudness < 0.003: # silence threshold, may need to adjus
        continue

    print("  sound captured | loudness: ", round(float(loudness), 4))