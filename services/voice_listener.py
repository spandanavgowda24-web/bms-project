import sounddevice as sd
import numpy as np
import whisper
import tempfile
from scipy.io.wavfile import write

# 🔥 LOAD ONLY ONCE (GLOBAL)
model = whisper.load_model("tiny")


def listen_command():

    sampleRate = 16000
    duration = 3   # 🔥 reduce from 4 → 3 (faster)

    print("Listening...")

    recording = sd.rec(
        int(duration * sampleRate),
        samplerate=sampleRate,
        channels=1,
        dtype='int16'
    )

    sd.wait()

    # 🔥 save temp audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, sampleRate, recording)

    # 🔥 transcribe
    result = model.transcribe(temp_file.name)

    text = result["text"].lower()

    print("You said:", text)

    return text