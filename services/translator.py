from googletrans import Translator

translator = Translator()

def translate_to_english(text):
    try:
        return translator.translate(text, dest="en").text
    except:
        return text