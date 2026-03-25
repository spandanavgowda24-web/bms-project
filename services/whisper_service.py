import whisper
import os
import re

print("Loading Whisper model...")

# 🔥 BEST BALANCE (accuracy + speed)
model = whisper.load_model("medium")

print("Whisper loaded")


def fix_language(text, detected_lang):
    """
    🔥 Smart correction for Indian languages
    """

    if re.search(r'[\u0C80-\u0CFF]', text):
        return "kn"

    if re.search(r'[\u0900-\u097F]', text):
        return "hi"

    if re.search(r'[\u0B80-\u0BFF]', text):
        return "ta"

    return detected_lang


def clean_text(text):
    """
    🔥 STRONG CLEANING (fix Kannada gaps issue)
    """

    # ❌ remove long gaps like ______ or ----
    text = re.sub(r'[_\-]{2,}', ' ', text)

    # ❌ remove weird repeated characters (Kannada stretching)
    text = re.sub(r'(.)\1{4,}', r'\1', text)

    # ❌ normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # ❌ remove duplicate words
    words = text.split()
    cleaned = []

    for w in words:
        if not cleaned or cleaned[-1] != w:
            cleaned.append(w)

    return " ".join(cleaned)


def transcribe_audio(audio_path):

    try:

        if not audio_path or not os.path.exists(audio_path):
            return {"text": "", "language": "unknown"}

        if os.path.getsize(audio_path) < 5000:
            return {"text": "", "language": "unknown"}

        # =========================
        # 🔥 STRONG TRANSCRIPTION SETTINGS
        # =========================
        result = model.transcribe(
            audio_path,
            fp16=False,
            task="transcribe",
            temperature=0.0,              # 🔥 stable output
            beam_size=8,                 # 🔥 better accuracy
            best_of=5,
            condition_on_previous_text=False
        )

        text = result.get("text", "").strip()
        lang = result.get("language", "unknown")

        print("🌍 ORIGINAL DETECTED:", lang)
        print("RAW:", text)

        # =========================
        # 🔥 LANGUAGE FIX
        # =========================
        lang = fix_language(text, lang)
        print("✅ FINAL LANGUAGE:", lang)

        # =========================
        # 🔥 CLEAN TEXT (BIG FIX)
        # =========================
        text = clean_text(text)

        # =========================
        # 🔥 QUALITY CHECK
        # =========================
        if len(text) < 15:
            print("❌ Too weak / unclear")
            return {"text": "", "language": lang}

        print("CLEAN:", text)

        return {
            "text": text,
            "language": lang
        }

    except Exception as e:
        print("❌ Whisper error:", e)
        return {"text": "", "language": "unknown"}