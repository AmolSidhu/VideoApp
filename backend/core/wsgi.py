"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

import videos.jobs as jobs

jobs.start_corruption_temp()
jobs.start_converter()
jobs.start_corruption_data()
jobs.start_imdb_data()
jobs.start_audio_profile()
jobs.start_visual_profile()
jobs.start_processing_completion()
jobs.start_failed_processing()
jobs.start_corruption_processing()

import management.jobs as jobs

jobs.start_identifiers()
jobs.start_json_record()
jobs.start_genre_check()