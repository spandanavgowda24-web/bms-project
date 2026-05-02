# services/translator_new.py - No dependency conflicts
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try different translation backends
try:
    # Option 1: deep-translator (more reliable)
    from deep_translator import GoogleTranslator

    translator = GoogleTranslator()
    USING_DEEP_TRANSLATOR = True
    logger.info("✅ Using deep-translator")
except ImportError:
    try:
        # Option 2: googletrans (if installed)
        from googletrans import Translator

        translator = Translator()
        USING_DEEP_TRANSLATOR = False
        logger.info("✅ Using googletrans")
    except ImportError:
        translator = None
        USING_DEEP_TRANSLATOR = False
        logger.warning("⚠️ No translator available - will return original text")


def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language"""
    if not text or not translator:
        return text

    if target_lang == 'en':
        return text

    try:
        if USING_DEEP_TRANSLATOR:
            result = GoogleTranslator(source='auto', target=target_lang).translate(text)
        else:
            result = translator.translate(text, dest=target_lang).text

        return result if result else text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text


def translate_list(texts: list, target_lang: str) -> list:
    """Translate a list of texts"""
    if not texts or not translator or target_lang == 'en':
        return texts

    results = []
    for text in texts:
        try:
            if USING_DEEP_TRANSLATOR:
                translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            else:
                translated = translator.translate(text, dest=target_lang).text
            results.append(translated if translated else text)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            results.append(text)

    return results