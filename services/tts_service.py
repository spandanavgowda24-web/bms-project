import asyncio
import edge_tts
import uuid
import os
from functools import lru_cache

OUTPUT_FOLDER = "tts_audio"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 🔥 HUMAN VOICES (BEST AVAILABLE)
VOICE_MAP = {
    "en_female": "en-IN-NeerjaNeural",
    "en_male": "en-IN-PrabhatNeural",
    "hi_female": "hi-IN-SwaraNeural",
    "hi_male": "hi-IN-MadhurNeural",
    "kn_female": "kn-IN-SapnaNeural",
    "kn_male": "kn-IN-GaganNeural"
}

# =========================
# 🔥 ASYNC EDGE (FASTER)
# =========================
async def edge_generate(text, voice, rate, path):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate
    )
    await communicate.save(path)


# =========================
# 🔥 CACHE (NO REPEAT GENERATION)
# =========================
@lru_cache(maxsize=100)
def cached_filename(text, language, voice, speed):
    return f"{hash(text+language+voice+speed)}.mp3"


# =========================
# 🔥 MAIN FUNCTION (FAST + STABLE)
# =========================
def generate_speech(text, language="en", voice="female", speed="normal"):

    if not text:
        return None

    text = text[:120]   # 🔥 SHORT = FAST RESPONSE

    filename = cached_filename(text, language, voice, speed)
    path = os.path.join(OUTPUT_FOLDER, filename)

    # 🔥 IF ALREADY GENERATED → INSTANT RESPONSE
    if os.path.exists(path):
        print("⚡ CACHE HIT")
        return filename

    selected_voice = VOICE_MAP.get(
        f"{language}_{voice}",
        "en-IN-NeerjaNeural"
    )

    rate_map = {
        "slow": "-20%",
        "normal": "+0%",
        "fast": "+25%"
    }

    rate = rate_map.get(speed, "+0%")

    # =========================
    # 🔥 EDGE TTS (PRIMARY)
    # =========================
    try:
        asyncio.run(edge_generate(text, selected_voice, rate, path))
        print("✅ EDGE:", selected_voice)
        return filename

    except Exception as e:
        print("❌ EDGE FAILED:", e)
        return None