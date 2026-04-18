from deep_translator import GoogleTranslator
import logging
import time

logger = logging.getLogger(__name__)

def translate_text(text, target_lang, source_lang='en'):
    if not text or not isinstance(text, str):
        return text
    try:
        # Add delay to avoid rate limiting (5 req/sec limit)
        time.sleep(0.5)
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

def translate_json_list(content_list, target_lang, source_lang='en'):
    if not content_list or not isinstance(content_list, list):
        return content_list
    
    translated_list = []
    for item in content_list:
        if isinstance(item, str):
            translated_list.append(translate_text(item, target_lang, source_lang))
        else:
            translated_list.append(item)
    return translated_list
