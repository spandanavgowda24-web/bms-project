import speech_recognition as sr


def transcribe_kannada(audio_path):

    try:

        r = sr.Recognizer()

        with sr.AudioFile(audio_path) as source:

            audio = r.record(source)

        text = r.recognize_google(audio, language="kn-IN")

        print("Kannada text:", text)

        return text

    except Exception as e:

        print("Kannada speech error:", e)

        return ""