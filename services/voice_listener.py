import sounddevice as sd
import numpy as np
import whisper
import tempfile
from scipy.io.wavfile import write
import os
import re

# =========================
# 🔥 LOAD MODEL (FASTEST + GOOD)
# =========================
model = whisper.load_model("base")   # 🔥 tiny → base (better accuracy)

# =========================
# 🔥 SMART CLEAN TEXT
# =========================
def clean_command(text):
    text = text.lower().strip()

    # remove noise words
    text = re.sub(r'[^\w\s]', '', text)

    # normalize
    text = re.sub(r'\s+', ' ', text)

    return text


# =========================
# 🔥 MAIN LISTENER (NO ECHO + FAST)
# =========================
def listen_command():

    sample_rate = 16000
    duration = 2.2   # 🔥 shorter = faster response

    print("🎤 Listening...")

    try:
        # 🔥 RECORD AUDIO
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )

        sd.wait()

        # =========================
        # 🔥 SILENCE DETECTION (BIG SPEED BOOST)
        # =========================
        volume = np.linalg.norm(recording)

        if volume < 100:
            print("🔇 Silence detected")
            return ""

        # =========================
        # 🔥 SAVE TEMP FILE
        # =========================
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            write(temp_file.name, sample_rate, recording)
            temp_path = temp_file.name

        # =========================
        # 🔥 FAST TRANSCRIBE
        # =========================
        result = model.transcribe(
            temp_path,
            fp16=False,
            temperature=0.0,
            condition_on_previous_text=False
        )

        os.remove(temp_path)

        text = result.get("text", "").strip()

        if not text:
            return ""

        text = clean_command(text)

        print("🧠 Heard:", text)

        return text

    except Exception as e:
        print("❌ Mic error:", e)
        return ""