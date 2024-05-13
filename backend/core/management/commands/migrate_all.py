from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    def handle(self, *args, **options):
        apps = [
            'user',
            'auth',
            'contenttypes',
            'sessions',
            'admin',
            'videos',
            'management',
            'stream'
            ]

        for app in apps:
            management.call_command('makemigrations', app)
            management.call_command('migrate', app)
            management.call_command('migrate', app, database='read_db')
