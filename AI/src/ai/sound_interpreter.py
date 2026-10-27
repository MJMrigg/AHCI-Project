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
import json
import sys

DEBUG = True
SR = 32000 # samples per sec
CALIBRATION_FILE = Path(__file__).parents[2] / "calibration.json"

SOUNDS = { # sound: AudioSet classes counted as sound
    "hum":      ["Humming"],
    "whistle":  ["Whistling", "Whistle", "Vehicle", "Sine wave"],
    "snap":     ["Finger snapping", "Clicking", "Plop"],
    "clap":     ["Clapping", "Hands", "Cap gun", "Chop", "Arrow", "Gunshot, gunfire"],
    "blow":     ["Wind", "Wind noise (microphone)", "Sigh", "Breathing"],
    "scratch":  ["Scratch", "Writing", "Rub"],
    "cough":    ["Cough", "Throat clearing"],
}

# Used if calibration is skipped
DEFAULT_SILENCE = 0.003
DEFAULT_THRESHOLDS = {"hum": 0.03, "whistle": 0.05, "snap": 0.12, "clap": 0.05, "blow": 0.05, "scratch": 0.05, "cough": 0.05}
DEFAULT_CUTOFFS = {"hum": 110, "whistle": 1200}

def record():
    audio = sd.rec(SR, samplerate=SR, channels=1, dtype="float32")
    sd.wait()
    return audio[:, 0]

def get_scores(model, audio):
    with torch.no_grad(): # disable gradient tracking
        return model(torch.from_numpy(audio[None]), None)["clipwise_output"][0].numpy()

def sound_score(scores, sound):
    return max(scores[labels.index(c)] for c in SOUNDS[sound])

def get_pitch(audio, fmin, fmax):
    f0, voiced, _ = librosa.pyin(audio, fmin=fmin, fmax=fmax, sr=SR)
    if voiced.mean() < 0.3: # no clear pitch
        return None
    return np.median(f0[voiced])

def calibrate(model):
    input("[CALIBRATE] Press Enter, then stay silent for 2 seconds.")
    background = [record(), record()]
    input("[CALIBRATE] Press Enter, then talk normally for 2 seconds.")
    background += [record(), record()]
    silence = 2 * min(np.sqrt(np.mean(a ** 2)) for a in background[:2])
    background_scores = [get_scores(model, a) for a in background]

    thresholds = {}
    for sound in SOUNDS:
        heard = []
        for i in range(3):
            input(f"[CALIBRATE] Press Enter, then {sound}. ({i+1}/3)")
            heard.append(sound_score(get_scores(model, record()), sound))
        noise = max(sound_score(s, sound) for s in background_scores)
        thresholds[sound] = max(0.6 * min(heard), 2 * noise, 0.01)
        print(f" {sound}: threshold {thresholds[sound]:.3f}")

    cutoffs = {}
    for sound, fmin, fmax in [("hum", 65, 1000), ("whistle", 400, 4000)]:
        pitches = []
        for level in ["LOW", "HIGH"]:
            pitch = None
            while pitch is None:
                input(f"[CALIBRATE] Press Enter, then {sound} {level} for a whole second.")
                pitch = get_pitch(record(), fmin, fmax)
                if pitch is None:
                    print("  No clear pitch, try again.")
            pitches.append(pitch)
        cutoffs[sound] = np.sqrt(pitches[0] * pitches[1])
        print(f"  {sound}: low {pitches[0]:.0f} Hz, high {pitches[1]:.0f} Hz, cutoff {cutoffs[sound]:.0f} Hz")

    return silence, thresholds, cutoffs

def load_or_calibrate(model):
    if "--calibrate" in sys.argv:
        silence, thresholds, cutoffs = calibrate(model)
        CALIBRATION_FILE.write_text(json.dumps({
            "silence": float(silence),
            "thresholds": {k: float(v) for k, v in thresholds.items()},
            "cutoffs": {k: float(v) for k, v in cutoffs.items()},
        }, indent=2))
        print(f"[CALIBRATE] Calibration saved to {CALIBRATION_FILE.name}.")
        return silence, thresholds, cutoffs
    if CALIBRATION_FILE.exists():
        data = json.loads(CALIBRATION_FILE.read_text())
        return data["silence"], data["thresholds"], data["cutoffs"]
    return DEFAULT_SILENCE, DEFAULT_THRESHOLDS, DEFAULT_CUTOFFS

def main():
    # Load model
    model_path = Path(__file__).parents[2] / "models" / "Cnn14_mAP=0.431.pth"
    if not model_path.exists():
        print("Model file not found. See AI/README.md for setup instructions.")
        return

    print("Loading sound model...")
    model = Cnn14(sample_rate=SR, window_size=1024, hop_size=320, mel_bins=64, fmin=50, fmax=14000, classes_num=527)
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    # Perform first pitch check since it's slow and could affect the game
    librosa.pyin(np.zeros(SR, dtype=np.float32), fmin=65, fmax=1000, sr=SR)

    silence, thresholds, cutoffs = load_or_calibrate(model)
    key_presser = KeyPresser()
    esc = Key.esc
    paused = False

    print("Listening...")
    try:
        while True:
            audio = record()

            # Skip silence
            if np.sqrt(np.mean(audio ** 2)) < silence:
                continue

            scores = get_scores(model, audio)

            confidence = {sound: sound_score(scores, sound) / thresholds[sound] for sound in SOUNDS}

            if(DEBUG):
                best = sorted(confidence, key=confidence.get, reverse=True)[:3]
                print("  " + " | ".join(f"{name} {confidence[name]:.2f}" for name in best))
                top = np.argsort(scores)[::-1][:3]
                print("  heard: " + ", ".join(f"{labels[i]} {scores[i]:.2f}" for i in top))

            sound = max(confidence, key=confidence.get)

            if confidence[sound] < 1:
                if DEBUG:
                    print(f"  [DEBUG] no input (best guess: {labels[np.argmax(scores)]})")
                continue

            if sound == "snap":
                loudness = librosa.feature.rms(y=audio, frame_length=512, hop_length=160)[0]
                peaks, _ = find_peaks(loudness, height=max(0.2 * loudness.max(), 4 * np.median(loudness)), distance=16)
                if len(peaks) >= 2:
                    sound = "double snap"

            # Differentiate between low/high hum/whistle
            if sound == "hum" or sound == "whistle":
                if sound == "hum":
                    pitch = get_pitch(audio, 65, 1000)
                else:
                    pitch = get_pitch(audio, 400, 4000)
                if pitch is None:
                    if DEBUG:
                        print(f"  [DEBUG] {sound} detected, but pitch was not identified")
                    continue
                if pitch < cutoffs[sound]:
                    sound = "low " + sound
                else:
                    sound = "high " + sound

            # Inputs
            if paused and sound not in ("snap", "double snap"):
                print(f"  [DEBUG] {sound} ignored (paused)")
                continue
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
                if paused:
                    key_presser.pause()
                else:
                    key_presser.unpause()
                print("  input: snap (pause/unpause)")
            elif sound == "clap":
                key_presser.press_once("f")
                print("  input: clap (fireball)")
            elif sound == "blow":
                key_presser.press_once("g")
                print("  input: blow (wind)")
            elif sound == "scratch":
                key_presser.press_once("t")
                print("  input: scratch (translate)")
            elif sound == "cough":
                key_presser.press_once("e")
                print("  input: cough (open)")
            elif sound == "double snap":
                if paused:
                    key_presser.press_once("q")
                    print("  input: double snap (quit)")
                    return
                else:
                    print("  input: double snap (ignored; only quits when paused)")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        key_presser.release_all()

if __name__ == "__main__":
    main()