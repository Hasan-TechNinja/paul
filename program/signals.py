import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Theme, Session, ThemeTranslation, SessionTranslation
from .utils import translate_text, translate_json_list

def run_theme_translation(instance_id):
    # Fetch instance again to be safe in thread
    instance = Theme.objects.filter(id=instance_id).first()
    if not instance:
        return

    supported_langs = getattr(settings, 'SUPPORTED_LANGUAGES', [])
    for lang_code, lang_name in supported_langs:
        try:
            translation, created_trans = ThemeTranslation.objects.get_or_create(
                theme=instance,
                language_code=lang_code
            )
            translation.title = translate_text(instance.title, lang_code)
            translation.description = translate_text(instance.description, lang_code)
            translation.intro_content = translate_json_list(instance.intro_content, lang_code)
            translation.save()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to translate theme {instance_id} to {lang_code}: {e}")

@receiver(post_save, sender=Theme)
def auto_translate_theme(sender, instance, created, **kwargs):
    # Run in background thread
    threading.Thread(target=run_theme_translation, args=(instance.id,)).start()

def run_session_translation(instance_id):
    instance = Session.objects.filter(id=instance_id).first()
    if not instance:
        return

    supported_langs = getattr(settings, 'SUPPORTED_LANGUAGES', [])
    for lang_code, lang_name in supported_langs:
        try:
            translation, created_trans = SessionTranslation.objects.get_or_create(
                session=instance,
                language_code=lang_code
            )
            translation.title = translate_text(instance.title, lang_code)
            translation.subtitle = translate_text(instance.subtitle, lang_code)
            translation.text_content = translate_json_list(instance.text_content, lang_code)
            translation.save()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to translate session {instance_id} to {lang_code}: {e}")

@receiver(post_save, sender=Session)
def auto_translate_session(sender, instance, created, **kwargs):
    # Run in background thread
    threading.Thread(target=run_session_translation, args=(instance.id,)).start()
