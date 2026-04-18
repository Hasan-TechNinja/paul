from django.core.management.base import BaseCommand
from program.models import Theme, Session
from program.signals import auto_translate_theme, auto_translate_session

class Command(BaseCommand):
    help = 'Translate all existing themes and sessions'

    def handle(self, *args, **options):
        self.stdout.write('Translating Themes...')
        themes = Theme.objects.all()
        for theme in themes:
            self.stdout.write(f'  Translating Theme: {theme.title}')
            auto_translate_theme(sender=Theme, instance=theme, created=False)
        
        self.stdout.write('Translating Sessions...')
        sessions = Session.objects.all()
        for session in sessions:
            # Check if all supported languages already exist
            from django.conf import settings
            supported_langs = [lang[0] for lang in settings.SUPPORTED_LANGUAGES]
            existing_langs = list(session.translations.values_list('language_code', flat=True))
            
            if all(lang in existing_langs for lang in supported_langs):
                self.stdout.write(f'  Skipping Session: {session.title} (All translations exist)')
                continue
                
            self.stdout.write(f'  Translating Session: {session.title}')
            auto_translate_session(sender=Session, instance=session, created=False)
        
        self.stdout.write(self.style.SUCCESS('All content translated successfully!'))
