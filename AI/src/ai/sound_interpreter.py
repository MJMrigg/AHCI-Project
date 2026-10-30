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
from key_press import KeyPresser
from pynput.keyboard import Key
import json
import sys

DEBUG = True
SR = 32000 # samples per sec
AI_DIR = Path(__file__).parents[2]
CALIBRATION_FILE = AI_DIR/"calibration.json"
MODEL_FILE = AI_DIR/"models"/"Cnn14_mAP=0.431.pth"
CALIBRATION_STEPS = 3

# Model is only used for action sounds; hums and whistles are found by pitch
SOUNDS = {
    "clap":     (["Clapping", "Hands", "Cap gun", "Chop", "Arrow", "Gunshot, gunfire", "Plop", "Slap, smack", "Hammer"], 0.12),
    "blow":     (["Wind", "Wind noise (microphone)", "Sigh", "Gasp", "Whoosh, swoosh, swish", "Breathing", "Snort"], 0.05),
    "cough":    (["Cough", "Throat clearing"], 0.05),
}

PITCH_RANGES = ["hum", "whistle"]
HUM_WHISTLE_SPLIT = 400 # Hz: below = hum, above = whistle

# Streaming
BLOCK = SR // 20 # 50 ms of new audio per loop
FRAME = 2048 # samples used for each pitch check (64 ms)
CLARITY = 0.8 # how clean the pitch has to be (0-1)
STEADY_FRAMES = 3 # blocks of steady pitch before moving
STEADY_RATIO = 1.06 # max pitch change between blocks
RELEASE_FRAMES = 2 # blocks without a tone before movement stops (100 ms)
ACTION_LEVEL = 2 # x silence: how loud a sound must get to be sent to the model
ACTION_WAIT = 10 # blocks to wait after a sound starts before classifying it (500 ms)

MOVE_KEYS = {"high hum": "w", "low hum": "s", "high whistle": "a", "low whistle": "d"}

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

def get_tone(frame):
    # Returns the pitch, or None if tone is not clean
    f0 = librosa.yin(frame, fmin=65, fmax=4000, sr=SR, frame_length=FRAME, center=False)[0]
    lag = int(round(SR / f0))
    a, b = frame[:-lag], frame[lag:]
    clarity = np.dot(a, b) / (np.sqrt(np.dot(a, a) * np.dot(b, b)) + 1e-10)
    if clarity < CLARITY:
        return None
    return f0


def get_pitch(audio):
    # Median tone over a longer recording (used by calibration)
    tones = [get_tone(audio[i:i + FRAME]) for i in range(0, len(audio) - FRAME, BLOCK)]
    tones = [t for t in tones if t is not None]
    if len(tones) < len(audio) // BLOCK // 3: # no clear pitch
        return None
    return np.median(tones)

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
    attempts = {} # scores for each attempt
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
            print(f"    [CAUTION] {sound} overlaps with another sound and may not always trigger")

    cutoffs = {}
    for sound in PITCH_RANGES:
        pitches = []
        for level in ["LOW", "HIGH"]:
            pitch = None
            while pitch is None:
                input(f"[CALIBRATE] Press Enter, then {sound} {level} for a whole second.")
                pitch = get_pitch(record())
                if pitch is None:
                    print("  No clear pitch, try again.")
            pitches.append(pitch)
        cutoffs[sound] = np.sqrt(pitches[0] * pitches[1])
        if sound == "hum" and pitches[1] > HUM_WHISTLE_SPLIT:
            print("    [CAUTION] high hum is above the hum/whistle split; hum lower")
        if sound == "whistle" and pitches[0] < HUM_WHISTLE_SPLIT:
            print("    [CAUTION] low whistle is below the hum/whistle split; whistle higher")
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

    # First model and pitch checks are slow, so they are called here to get them out of the way
    get_scores(model, np.zeros(SR, dtype=np.float32))
    get_tone(np.random.default_rng(0).normal(0, 0.01, FRAME).astype(np.float32))

    silence, thresholds, cutoffs = load_or_calibrate(model)
    key_presser = KeyPresser()
    paused = False

    buffer = np.zeros(SR, dtype=np.float32) # last 1 second of audio
    tones = [] # pitch of recent blocks (None = no tone)
    moving = None # movement key currently held down
    quiet_frames = 0 # blocks in a row without a tone while moving
    was_loud = False
    action_wait = 0 # blocks left before the current sound gets classified
    action_tones = 0 # tone blocks while waiting

    print("Listening...")
    stream = sd.InputStream(samplerate=SR, channels=1, dtype="float32", blocksize=BLOCK)
    stream.start()
    try:
        while True:
            block, _ = stream.read(BLOCK)
            buffer = np.concatenate([buffer[BLOCK:], block[:, 0]])
            frame = buffer[-FRAME:]
            loud = loudness(block[:, 0]) > ACTION_LEVEL * silence

            # Movement (hum/whistle by pitch)
            tone = get_tone(frame) if loudness(frame) > silence else None
            tones = (tones + [tone])[-STEADY_FRAMES:]

            sound = None
            if tone is not None:
                sound = "whistle" if tone > HUM_WHISTLE_SPLIT else "hum"
                sound = ("low " if tone < cutoffs[sound] else "high ") + sound

            if moving is None:
                # Start only when the pitch has been steady for a moment
                steady = None not in tones and len(tones) == STEADY_FRAMES and max(tones) / min(tones) < STEADY_RATIO
                if steady and not paused:
                    moving = MOVE_KEYS[sound]
                    quiet_frames = 0
                    key_presser.press(moving)
                    print(f"  input: {sound} ({tone:.0f} Hz) -> hold {moving}")
            elif tone is None:
                # Stop after the tone has been gone for a moment
                quiet_frames += 1
                if quiet_frames >= RELEASE_FRAMES:
                    key_presser.release(moving)
                    print(f"  input: release {moving}")
                    moving = None
            else:
                quiet_frames = 0  # still holding the tone; direction stays the same until it stops

            # Actions: model on sounds that suddenly start
            classify = False
            if action_wait > 0:
                action_wait -= 1
                if tone is not None:
                    action_tones += 1
                classify = action_wait == 0
            elif loud and not was_loud and tone is None and moving is None:
                action_wait = ACTION_WAIT # sound started; wait for rest of the sound
                action_tones = 0
            was_loud = loud

            if not classify:
                continue
            if action_tones >= 3: # it turned into a hum/whistle
                if DEBUG:
                    print("  [DEBUG] action skipped (uncertain)")
                continue

            audio = buffer # 0.5 s before the sound started + 0.5 s after
            scores = get_scores(model, audio)
            confidence = {sound: sound_score(scores, sound) / thresholds[sound] for sound in SOUNDS}

            if DEBUG:
                best = sorted(confidence, key=confidence.get, reverse=True)[:3]
                print("  " + " | ".join(f"{name} {confidence[name]:.2f}" for name in best))
                top = np.argsort(scores)[::-1][:3]
                print("  heard: " + ", ".join(f"{labels[i]} {scores[i]:.2f}" for i in top))

            sound = max(confidence, key=confidence.get)

            if confidence[sound] < 1:
                if DEBUG:
                    print(f"  [DEBUG] no input")
                continue

            if sound == "clap":
                envelope = librosa.feature.rms(y=audio[SR * 2 // 5:], frame_length=512, hop_length=160)[0]
                peaks, _ = find_peaks(envelope, height=max(0.2 * envelope.max(), 4 * np.median(envelope)), distance=30)
                if DEBUG:
                    print("  [DEBUG] peaks at " + ", ".join(
                        f"{0.4 + p * 0.005:.2f}s ({envelope[p] / envelope.max():.2f})" for p in peaks))
                if len(peaks) >= 2:
                    sound = "double clap"

            if sound == "blow" and loud:  # still blowing 0.5 s after it started
                sound = "long blow"

            # Inputs
            if paused and sound not in ("clap", "double clap"):
                if DEBUG:
                    print(f"  [DEBUG] {sound} ignored (paused)")
                continue
            if sound == "double clap" and not paused:
                if moving is not None:
                    key_presser.release(moving)
                    moving = None
                key_presser.press_once(Key.esc)
                paused = True
                print("  input: double clap (pause)")
            elif sound == "clap" and paused:
                key_presser.press_once(Key.esc)
                paused = False
                print("  input: clap (resume)")
            elif sound == "double clap" and paused:
                key_presser.press_once("q")
                print("  input: double clap (quit)")
                return
            elif sound == "clap":
                key_presser.press_once("f")
                print("  input: clap (fireball)")
            elif sound == "blow":
                key_presser.press_once("g")
                print("  input: short puff (wind)")
            elif sound == "long blow":
                key_presser.press_once("t")
                print("  input: long blow (translate)")
            elif sound == "cough":
                key_presser.press_once("e")
                print("  input: cough (open)")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        stream.stop()
        stream.close()
        key_presser.release_all()

if __name__ == "__main__":
    main()