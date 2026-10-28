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
AI_DIR = Path(__file__).parents[2]
CALIBRATION_FILE = AI_DIR/"calibration.json"
MODEL_FILE = AI_DIR/"models"/"Cnn14_mAP=0.431.pth"
CALIBRATION_STEPS = 3

SOUNDS = {
    "hum":      (["Humming", "Chant", "Singing bowl", "Mantra", "Moo", "Cattle, bovinae"], 0.03),
    "whistle":  (["Whistling", "Whistle", "Sine wave", "Siren", "Beep, bleep"], 0.05),
    #"snap":     (["Finger snapping", "Clicking"], 0.08),
    "knock":    (["Knock", "Tap", "Thump, thud"], 0.06),
    "clap":     (["Clapping", "Hands", "Cap gun", "Chop", "Arrow", "Gunshot, gunfire", "Plop", "Slap, smack", "Hammer"], 0.12),
    "blow":     (["Wind", "Wind noise (microphone)", "Sigh", "Gasp", "Whoosh, swoosh, swish", "Breathing"], 0.05),
    "scratch":  (["Scratch", "Writing", "Rub"], 0.05),
    "cough":    (["Cough", "Throat clearing"], 0.05),
}

PITCH_RANGES = {"hum": (65, 1000), "whistle": (400, 4000)} # Hz range
HUM_WHISTLE_SPLIT = 400 # Hz: below = hum, above = whistle

# Used if calibration is skipped
DEFAULT_SILENCE = 0.01
DEFAULT_THRESHOLDS = {sound: default for sound, (classes, default) in SOUNDS.items()}
DEFAULT_CUTOFFS = {"hum": 110, "whistle": 1200}

def record():
    audio = sd.rec(SR, samplerate=SR, channels=1, dtype="float32")
    sd.wait()
    return audio[:, 0]

def get_scores(model, audio):
    with torch.no_grad(): # disable gradient tracking
        return model(torch.from_numpy(audio[None]), None)["clipwise_output"][0].numpy()

def sound_score(scores, sound):
    return max(scores[labels.index(c)] for c in SOUNDS[sound][0])

def get_pitch(audio, fmin, fmax):
    f0, voiced, _ = librosa.pyin(audio, fmin=fmin, fmax=fmax, sr=SR)
    if voiced.mean() < 0.3: # no clear pitch
        return None
    return np.median(f0[voiced])

def loudness(audio):
    return librosa.feature.rms(y=audio, frame_length=1024, hop_length=512)[0].max()

def calibrate(model):
    input("[CALIBRATE] Press Enter, then stay silent for 2 seconds.")
    background = [record(), record()]
    input("[CALIBRATE] Press Enter, then talk normally for 2 seconds.")
    background += [record(), record()]
    silence = 2 * min(loudness(a) for a in background[:2])
    background_scores = [get_scores(model, a) for a in background]

    # Record every sound first, so each threshold can account for the others
    attempts = {} # sound -> score arrays from each attempt
    for sound in SOUNDS:
        attempts[sound] = []
        for i in range(CALIBRATION_STEPS):
            input(f"[CALIBRATE] Press Enter, then {sound}. ({i+1}/{CALIBRATION_STEPS})")
            attempts[sound].append(get_scores(model, record()))

    thresholds = {}
    for sound in SOUNDS:
        heard = [sound_score(s, sound) for s in attempts[sound]]
        others = [sound_score(s, sound) for other in SOUNDS if other != sound for s in attempts[other]]
        noise = max(sound_score(s, sound) for s in background_scores)
        thresholds[sound] = max(0.5 * min(heard), 1.2 * max(others), 2 * noise, 0.5 * SOUNDS[sound][1])
        thresholds[sound] = min(thresholds[sound], 3 * SOUNDS[sound][1])
        print(f" {sound}: threshold {thresholds[sound]:.3f}")
        if thresholds[sound] > min(heard):
            print(f"  WARNING: {sound} overlaps with another sound and may not always trigger")

    cutoffs = {}
    for sound, (fmin, fmax) in PITCH_RANGES.items():
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
        print(f"[CALIBRATE] Loading saved calibration configs...")
        return data["silence"], data["thresholds"], data["cutoffs"]
    print(f"[CALIBRATE] Loading default calibration configs...")
    return DEFAULT_SILENCE, DEFAULT_THRESHOLDS, DEFAULT_CUTOFFS

def main():
    # Load model
    if not MODEL_FILE.exists():
        print("Model file not found. See AI/README.md for setup instructions.")
        return

    print("Loading sound model...")
    model = Cnn14(sample_rate=SR, window_size=1024, hop_size=320, mel_bins=64, fmin=50, fmax=14000, classes_num=527)
    checkpoint = torch.load(MODEL_FILE, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    # Perform first pitch check since it's slow and could affect the game
    librosa.pyin(np.zeros(SR, dtype=np.float32), fmin=65, fmax=1000, sr=SR)

    silence, thresholds, cutoffs = load_or_calibrate(model)
    key_presser = KeyPresser()
    paused = False

    print("Listening...")
    try:
        while True:
            audio = record()

            # Skip silence
            if loudness(audio) < silence:
                continue

            scores = get_scores(model, audio)

            confidence = {sound: sound_score(scores, sound) / thresholds[sound] for sound in SOUNDS}

            if DEBUG:
                best = sorted(confidence, key=confidence.get, reverse=True)[:3]
                print("  " + " | ".join(f"{name} {confidence[name]:.2f}" for name in best))
                top = np.argsort(scores)[::-1][:3]
                print("  heard: " + ", ".join(f"{labels[i]} {scores[i]:.2f}" for i in top))
                print("  raw: " + " | ".join(f"{s} {sound_score(scores, s):.3f}" for s in SOUNDS))

            sound = max(confidence, key=confidence.get)

            if confidence[sound] < 1:
                if DEBUG:
                    print(f"  [DEBUG] no input")
                continue

            if sound == "knock":
                envelope = librosa.feature.rms(y=audio, frame_length=512, hop_length=160)[0]
                peaks, _ = find_peaks(envelope, height=max(0.2 * envelope.max(), 4 * np.median(envelope)), distance=16)
                if len(peaks) >= 2:
                    sound = "double knock"

            # Hum/whistle: pitch decides which and whether low/high
            if sound in ("hum", "whistle", "blow"):
                pitch = get_pitch(audio, 65, 4000)
                if pitch is not None and (sound != "blow" or pitch > HUM_WHISTLE_SPLIT):
                    sound = "whistle" if pitch > HUM_WHISTLE_SPLIT else "hum"
                    sound = ("low " if pitch < cutoffs[sound] else "high ") + sound
                elif sound != "blow":
                    if DEBUG:
                        print(f"  [DEBUG] {sound} detected, but pitch was not identified")
                    continue

            # Inputs
            if paused and sound not in ("knock", "double knock"):
                if DEBUG:
                    print(f"  [DEBUG] {sound} ignored (paused)")
                continue
            if sound == "high hum":
                key_presser.toggle("w")
                print("  input: high hum (up)")
            elif sound == "low hum":
                key_presser.toggle("s")
                print("  input: low hum (down)")
            elif sound == "high whistle":
                key_presser.toggle("a")
                print("  input: high whistle (left)")
            elif sound == "low whistle":
                key_presser.toggle("d")
                print("  input: low whistle (right)")
            elif sound == "knock":
                key_presser.press_once(Key.esc)
                paused = not paused
                print("  input: knock (pause/unpause)")
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
            elif sound == "double knock":
                if paused:
                    key_presser.press_once("q")
                    print("  input: double knock (quit)")
                    return
                else:
                    print("  input: double knock (ignored; only quits when paused)")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        key_presser.release_all()

if __name__ == "__main__":
    main()