# Note: This file will NOT run without installing the necessary files.
# See README.md for installation instructions.

import numpy as np
import sounddevice as sd
from panns_inference import labels
from panns_inference.models import Cnn14
from pathlib import Path
import torch

SR = 32000 # samples per sec

model = Cnn14(sample_rate=SR, window_size=1024, hop_size=320, mel_bins=64, fmin=50, fmax=14000, classes_num=527)
checkpoint = torch.load(Path(__file__).parents[2] / "models" / "Cnn14_mAP=0.431.pth", map_location="cpu", weights_only=False)
model.load_state_dict(checkpoint["model"])
model.eval()

print("Listening...")
while True:
    audio = sd.rec(SR, samplerate=SR, channels=1, dtype="float32")
    sd.wait()
    audio = audio[:, 0]

    if np.sqrt(np.mean(audio ** 2)) < 0.003: # silence threshold, may need to adjust
        continue

    with torch.no_grad(): # disable gradient tracking
        scores = model(torch.from_numpy(audio[None]), None)["clipwise_output"][0].numpy()

    # best = np.argmax(scores)
    # print(f"  heard: {labels[best]} ({scores[best]:.2f})")

    def score(name):
        return scores[labels.index(name)]

    th = 0.3 # threshold

    if score("Humming") > th or score("Hum") > th: # in progress: differentiate high/low hum
        print("  input: hum")
    if score("Whistling") > th or score("Whistle") > th: # in progress: differentiate high/low whistle
        print("  input: whistle")
    if score("Finger snapping") > th: # Pause (esc)
        print("  input: snap")
    if score("Clapping") > th or score("Hands") > th: # Fireball (F)
        print("  input: clap")
    if score("Wind") > th or score("Wind noise (microphone)") > th: # Gust (G)
        print("  input: blow")
    if score("Clicking") > th: # Translate (F)
        print("  input: click")
    if score("Burst, pop") > th: # Open/Close (E)
        print("  input: pop")
    if score("Meow") > th: # Quit (Q)
        print("  input: meow")
    
    else:
        print(f"  no input assigned: {labels[np.argmax(scores)]}")