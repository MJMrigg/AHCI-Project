# Note: This file will NOT run without installing the necessary files.
# See README.md for installation instructions.

import numpy as np
import sounddevice as sd
from panns_inference import labels
from panns_inference.models import Cnn14
from pathlib import Path
import torch
import librosa
from scipy.signal import find_peaks
from key_press import KeyPresser # will switch to ai.key_press once voice is contained in a main function
from pynput.keyboard import Key

SR = 32000 # samples per sec

def main():
    # Load model
    model = Cnn14(sample_rate=SR, window_size=1024, hop_size=320, mel_bins=64, fmin=50, fmax=14000, classes_num=527)
    checkpoint = torch.load(Path(__file__).parents[2] / "models" / "Cnn14_mAP=0.431.pth", map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    # Perform first pitch check since it's slow and could affect the game
    librosa.pyin(np.zeros(SR, dtype=np.float32), fmin=65, fmax=1000, sr=SR)

    key_presser = KeyPresser()
    esc = Key.esc
    paused = False
    last_sound = None

    print("Listening...")
    while True:
        previous_sound = last_sound
        last_sound = None

        # Get one second of audio
        audio = sd.rec(SR, samplerate=SR, channels=1, dtype="float32")
        sd.wait()
        audio = audio[:, 0]

        # Skip silence
        if np.sqrt(np.mean(audio ** 2)) < 0.003:
            continue

        with torch.no_grad(): # disable gradient tracking
            scores = model(torch.from_numpy(audio[None]), None)["clipwise_output"][0].numpy()

        def score(name):
            return scores[labels.index(name)]

        confidence = {
            "hum": score("Humming") / 0.03,
            "whistle": max(score("Whistling") / 0.05, score("Whistle") / 0.05, score("Vehicle") / 0.05,
                           score("Sine wave") / 0.05),
            "snap": score("Finger snapping") / 0.15,
            "clap": max(score("Clapping") / 0.08, score("Hands") / 0.05, score("Cap gun") / 0.05,
                        score("Arrow") / 0.05),
            "blow": max(score("Wind") / 0.05, score("Wind noise (microphone)") / 0.2, score("Sigh") / 0.2,
                        score("Breathing") / 0.05),
            "click": max(score("Clicking") / 0.05, score("Plop") / 0.05),
            "cough": max(score("Cough") / 0.15, score("Throat clearing") / 0.05),
        }

        print("  ", {name: round(float(c), 2) for name, c in confidence.items()})

        sound = max(confidence, key=confidence.get)
        if confidence[sound] < 1:
            print(f"  no input (best guess: {labels[np.argmax(scores)]})")
            continue

        if sound == "snap":
            loudness = librosa.feature.rms(y=audio, frame_length=512, hop_length=160)[0]
            peaks, _ = find_peaks(loudness, height=max(0.2 * loudness.max(), 4 * np.median(loudness)), distance=16)
            if len(peaks) >= 2:
                sound = "double snap"

        # Differentiate between low/high hum/whistle
        if sound == "hum" or sound == "whistle":
            if sound == "hum":
                f0, voiced, _ = librosa.pyin(audio, fmin=65, fmax=1000, sr=SR)
                cutoff = 110
            else:
                f0, voiced, _ = librosa.pyin(audio, fmin=400, fmax=4000, sr=SR)
                cutoff = 1200
            pitched = voiced.mean()
            if pitched < 0.3:  # no clear pitch
                continue
            pitch = np.median(f0[voiced])
            if pitch < cutoff:
                sound = "low " + sound
            else:
                sound = "high " + sound

        last_sound = sound
        if sound == previous_sound and ("hum" in sound or "whistle" in sound):
            continue # same hum/whistle across clips won't retrigger

        # Inputs
        if sound == "high hum":
            key_presser.release("s")
            key_presser.toggle("w")
            print("  input: high hum (up)")
        elif sound == "low hum":
            key_presser.release("w")
            key_presser.toggle("s")
            print("  input: low hum (down)")
        elif sound == "high whistle":
            key_presser.release("d")
            key_presser.toggle("a")
            print("  input: high whistle (left)")
        elif sound == "low whistle":
            key_presser.release("a")
            key_presser.toggle("d")
            print("  input: low whistle (right)")
        elif sound == "snap":
            key_presser.press_once(esc)
            paused = not paused
            print("  input: snap (pause/unpause)")
        elif sound == "clap":
            key_presser.press_once("f")
            print("  input: clap (fireball)")
        elif sound == "blow":
            key_presser.press_once("g")
            print("  input: blow (wind)")
        elif sound == "click":
            key_presser.press_once("t")
            print("  input: click (translate)")
        elif sound == "cough":
            key_presser.press_once("e")
            print("  input: cough (open)")
        elif sound == "double snap":
            if paused:
                key_presser.press_once("q")
                for key in ["w", "s", "a", "d", esc, "f", "g", "t", "e","q"]:
                    key_presser.release(key)
                print("  input: double snap (quit)")
                quit()
            else:
                print("  double snap ignore (only quits when paused)")

if __name__ == "__main__":
    main()