# coding: utf-8

# imports
import os

# django imports
from django.conf import settings

TWISTRANET_MEDIA_ROOT = getattr(settings, "TWISTRANET_MEDIA_ROOT", settings.MEDIA_ROOT)
TWISTRANET_MEDIA_URL = getattr(settings, "TWISTRANET_MEDIA_URL", settings.MEDIA_URL)
FILE_UPLOAD_PERMISSIONS = getattr(settings, "FILE_UPLOAD_PERMISSIONS", None)