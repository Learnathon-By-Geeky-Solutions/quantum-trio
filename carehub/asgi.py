"""
ASGI config for carehub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv  # <-- Add this line
from django.core.asgi import get_asgi_application

load_dotenv()  # <-- And this line to load .env variables

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carehub.settings')

application = get_asgi_application()
