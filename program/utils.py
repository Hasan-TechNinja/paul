from deep_translator import GoogleTranslator
import logging
import time
from django.conf import settings

# Google API Discovery Client for Paid Translation
try:
    from googleapiclient.discovery import build
except ImportError:
    build = None

logger = logging.getLogger(__name__)

def translate_text(text, target_lang, source_lang='en'):
    if not text or not isinstance(text, str):
        return text

    # Try using Paid Google API (v2) if key is available
    google_api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if google_api_key and build:
        try:
            # Using developerKey for API Key authentication
            service = build('translate', 'v2', developerKey=google_api_key)
            result = service.translations().list(q=[text], target=target_lang).execute()
            
            if 'translations' in result and len(result['translations']) > 0:
                translated_text = result['translations'][0]['translatedText']
                # Google API might return HTML entities (like &#39; for apostrophe)
                import html
                return html.unescape(translated_text)
        except Exception as e:
            logger.error(f"Paid Google Translation error: {e}")
            # Fallback to free translator below

    # Free fallback using deep-translator
    try:
        # Add delay to avoid rate limiting for free service (5 req/sec limit)
        time.sleep(0.5)
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        logger.error(f"Translation error (free fallback): {e}")
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
