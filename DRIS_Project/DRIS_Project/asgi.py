# Name: Amir Ali Malekani Nezhad
# Student ID: S2009460

"""
ASGI config for DRIS_Project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application # type: ignore

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DRIS_Project.settings")

application = get_asgi_application()
