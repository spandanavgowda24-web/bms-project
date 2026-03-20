from gtts import gTTS
import uuid
import os

OUTPUT_FOLDER = "tts_audio"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


def generate_speech(text, language):

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    # language mapping
    lang_map = {
        "en": "en",
        "hi": "hi",
        "kn": "kn"
    }

    tts = gTTS(text=text, lang=lang_map.get(language, "en"))

    tts.save(filepath)

    return filename