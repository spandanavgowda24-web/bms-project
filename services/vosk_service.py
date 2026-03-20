from vosk import Model, KaldiRecognizer
import wave
import json

print("Loading Vosk model...")

model_hi = Model("models/vosk-model-small-hi-0.22")

print("Vosk model loaded")


def transcribe_vosk(audio_path, language):

    wf = wave.open(audio_path, "rb")

    recognizer = KaldiRecognizer(model_hi, wf.getframerate())

    text = ""

    while True:

        data = wf.readframes(4000)

        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):

            result = json.loads(recognizer.Result())

            text += result.get("text", "") + " "

    final = json.loads(recognizer.FinalResult())

    text += final.get("text", "")

    print("Vosk text:", text)

    return text.strip()