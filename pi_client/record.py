"""
Records a short audio clip and saves it as clip.wav
Run this to make test audio for EchoMind.
"""

import sounddevice as sd
import soundfile as sf

SECONDS = 8
OUT = "clip.wav"

print(f"Recording for {SECONDS} seconds... speak clearly.")

audio = sd.rec(int(SECONDS * 16000), samplerate=16000, channels=1)
sd.wait()

sf.write(OUT, audio, 16000)
print("Saved:", OUT)