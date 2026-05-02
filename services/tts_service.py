import asyncio
import edge_tts
import os
import hashlib
import pyttsx3

OUTPUT_FOLDER = "tts_audio"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

engine = pyttsx3.init()

# 🔥 FIX: better voice mapping
VOICE_MAP = {
    "en_female": "en-IN-NeerjaNeural",
    "en_male": "en-IN-PrabhatNeural",
    "hi_female": "hi-IN-SwaraNeural",
    "hi_male": "hi-IN-MadhurNeural",
    "kn_female": "kn-IN-SapnaNeural",
    "kn_male": "kn-IN-GaganNeural"
}


# =========================
# CLEAN TEXT
# =========================
def clean_for_tts(text):
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:150]   # ✅ allow more words


# =========================
# CACHE FILE
# =========================
def get_filename(text, lang, voice, speed):
    key = f"{text}_{lang}_{voice}_{speed}"
    return hashlib.md5(key.encode()).hexdigest() + ".mp3"


# =========================
# EDGE TTS
# =========================
async def edge_generate(text, voice, rate, path):
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate
        )
        await communicate.save(path)
        return True
    except Exception as e:
        print("❌ EDGE FAIL:", e)
        return False


# =========================
# OFFLINE TTS (FIXED)
# =========================
def offline_tts(text, path):
    try:
        engine.setProperty('rate', 170)  # ✅ speed fix
        engine.save_to_file(text, path)
        engine.runAndWait()

        if os.path.exists(path):
            return True

    except Exception as e:
        print("❌ OFFLINE FAIL:", e)

    return False


# =========================
# MAIN FUNCTION (FIXED)
# =========================
def generate_speech(text, language="en", voice="female", speed="normal"):

    if not text:
        return None

    text = clean_for_tts(text)

    filename = get_filename(text, language, voice, speed)
    path = os.path.join(OUTPUT_FOLDER, filename)

    # ✅ CACHE HIT
    if os.path.exists(path):
        print("⚡ USING CACHED AUDIO")
        return filename

    # 🔥 SAFE LANGUAGE
    if language not in ["en", "hi", "kn"]:
        language = "en"

    selected_voice = VOICE_MAP.get(
        f"{language}_{voice}",
        "en-IN-NeerjaNeural"
    )

    rate_map = {
        "slow": "-15%",
        "normal": "+0%",
        "fast": "+15%"
    }

    rate = rate_map.get(speed, "+0%")

    # =========================
    # TRY EDGE TTS
    # =========================
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        success = loop.run_until_complete(
            edge_generate(text, selected_voice, rate, path)
        )

        loop.close()

        if success and os.path.exists(path):
            print("✅ EDGE AUDIO SUCCESS")
            return filename

    except Exception as e:
        print("❌ EDGE ERROR:", e)

    # =========================
    # 🔥 FALLBACK (ALWAYS SPEAK)
    # =========================
    print("⚡ USING OFFLINE VOICE")

    if offline_tts(text, path):
        return filename

    print("❌ TOTAL TTS FAILED")
    return None