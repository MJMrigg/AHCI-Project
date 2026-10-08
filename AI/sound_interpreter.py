import numpy as np
import sounddevice as sd
from panns_inference import labels
from panns_inference.models import Cnn14
from pathlib import Path
import torch

SR = 32000 # samples per sec

model = Cnn14(sample_rate=SR, window_size=1024, hop_size=320, mel_bins=64, fmin=50, fmax=14000, classes_num=527)
checkpoint = torch.load(Path(__file__).parent / "models" / "Cnn14_mAP=0.431.pth", map_location="cpu", weights_only=False)
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

    best = np.argmax(scores)
    print(f"  heard: {labels[best]} ({scores[best]:.2f})")