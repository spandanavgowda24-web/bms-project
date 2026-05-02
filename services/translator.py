# services/translator.py - COMPLETE FIX for HI and KN translations
import time
import logging
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Use Google Translate API directly (most reliable)
class SimpleGoogleTranslator:
    """Simple Google Translate using direct API calls"""

    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
        logger.info("✅ Using Google Translate API")

    def translate(self, text, target_lang, source_lang='auto'):
        """Translate text using Google Translate API"""
        if not text or not text.strip():
            return text

        # If target is English, return original
        if target_lang == 'en':
            return text

        try:
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                result = response.json()
                # Extract translated text from response
                if result and len(result) > 0:
                    translated = ''.join([part[0] for part in result[0] if part[0]])
                    return translated if translated else text

            logger.warning(f"Translation API returned {response.status_code}")
            return text

        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def translate_batch(self, texts, target_lang, source_lang='auto'):
        """Translate multiple texts"""
        if not texts or target_lang == 'en':
            return texts

        results = []
        for text in texts:
            translated = self.translate(text, target_lang, source_lang)
            results.append(translated)
            time.sleep(0.1)  # Small delay to avoid rate limiting

        return results


# Try different translation backends in order of reliability
translator = None
translation_method = None

# First try: Simple Google Translate API (most reliable, no dependencies)
try:
    translator = SimpleGoogleTranslator()
    translation_method = "google_api"
    logger.info("✅ Using Google Translate API for translations")
except Exception as e:
    logger.warning(f"Google API failed: {e}")

    # Second try: deep-translator
    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator()
        translation_method = "deep"
        logger.info("✅ Using deep-translator")
    except ImportError:
        # Third try: googletrans
        try:
            from googletrans import Translator

            translator = Translator()
            translation_method = "google"
            logger.info("✅ Using googletrans")
        except ImportError:
            translator = None
            translation_method = "none"
            logger.warning("⚠️ No translator available - will return original text")

# Language mapping
LANGUAGE_MAP = {
    'en': 'english',
    'hi': 'hindi',
    'kn': 'kannada'
}

# Language codes for Google API
LANG_CODES = {
    'en': 'en',
    'hi': 'hi',
    'kn': 'kn'
}


def translate_to_english(text):
    """Translate any text to English"""
    if not text or translation_method == "none":
        return text

    try:
        if translation_method == "google_api":
            return translator.translate(text, 'en')
        elif translation_method == "deep":
            result = translator.translate(text, source='auto', target='en')
            return result if result else text
        else:
            res = translator.translate(text, dest="en")
            return res.text if res and res.text else text
    except Exception as e:
        logger.error(f"Translate error: {e}")
        return text


def translate_list(text_list, dest_lang):
    """
    Translate a list of texts to destination language
    Supports: 'en', 'hi', 'kn'
    """
    if not text_list or translation_method == "none":
        return text_list

    # If target is English, return original (no translation needed)
    if dest_lang == 'en':
        return text_list

    logger.info(f"Translating {len(text_list)} items to {dest_lang}")

    results = []

    for i, t in enumerate(text_list):
        if not t or len(t.strip()) < 3:
            results.append(t)
            continue

        try:
            if translation_method == "google_api":
                translated = translator.translate(t, dest_lang)
                results.append(translated if translated else t)
            elif translation_method == "deep":
                translated = translator.translate(t, source='auto', target=dest_lang)
                results.append(translated if translated else t)
            else:
                res = translator.translate(t, dest=dest_lang)
                results.append(res.text if res and res.text else t)

            # Small delay to prevent rate limiting
            if i % 5 == 0:  # Delay every 5 items
                time.sleep(0.2)

        except Exception as e:
            logger.error(f"Translate error for '{dest_lang}': {e}")
            results.append(t)

    logger.info(f"Translation complete: {len(results)} items")
    return results


def translate_bulk(text_list, dest_lang):
    """Bulk translation for better performance"""
    if not text_list or translation_method == "none" or dest_lang == 'en':
        return text_list

    try:
        if translation_method == "google_api":
            return translator.translate_batch(text_list, dest_lang)
        elif translation_method == "deep":
            results = []
            for text in text_list:
                translated = translator.translate(text, source='auto', target=dest_lang)
                results.append(translated if translated else text)
            return results
        else:
            res = translator.translate(text_list, dest=dest_lang)
            if isinstance(res, list):
                return [r.text if r and r.text else text_list[i] for i, r in enumerate(res)]
            return text_list
    except Exception as e:
        logger.error(f"Bulk translate error: {e}")
        return text_list


def get_supported_languages():
    """Return list of supported languages"""
    return ['en', 'hi', 'kn']


def get_language_name(lang_code):
    """Convert language code to full name"""
    names = {
        'en': 'English',
        'hi': 'हिन्दी (Hindi)',
        'kn': 'ಕನ್ನಡ (Kannada)'
    }
    return names.get(lang_code, 'English')


# Test function
if __name__ == "__main__":
    test_texts = [
        "First, boil 2 cups of water in a pot.",
        "Then, add 2 teaspoons of tea leaves.",
        "Finally, serve hot."
    ]

    print("\n=== Testing Translations ===\n")
    print(f"English: {test_texts[0]}")
    print(f"Hindi: {translate_list(test_texts[:1], 'hi')[0]}")
    print(f"Kannada: {translate_list(test_texts[:1], 'kn')[0]}")