#!/usr/bin/env python
# Record consent audio from microphone
# Press Ctrl+C to stop recording

import wave
import sys

try:
    import pyaudio
except ImportError:
    print("Installing pyaudio...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
    import pyaudio

RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024
OUTPUT = "consent_joey.wav"

print("=" * 50)
print("Please read aloud:")
print()
print('  "I, Joey Zeng, am aware that recordings')
print('   of my voice will be used by Microsoft')
print('   to create and use a synthetic version')
print('   of my voice."')
print()
print("Recording... Press Ctrl+C to stop.")
print("=" * 50)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

frames = []
try:
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(OUTPUT, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"\nSaved to {OUTPUT} ({len(frames) * CHUNK / RATE:.1f}s)")
