# -*- coding: utf-8 -*-
"""
This is used to translate the EN version into FR
"""
from twistranet.models import *
from twistranet.lib.python_fixture import Fixture
from twistrans.models import *

try:
    __account__ = SystemAccount.get()
except:
    print "SystemAccount not set yet"

FIXTURES = [
    Fixture(
        TranslationResource,
        force_update = True,
        slug = "help_title_fr",
        language = "fr-fr",
        original = Document.objects.filter(slug = "help"),
        original_field = "title",
        translated_text = "Aide de TwistraNet",
    ),
    
    Fixture(
        TranslationResource,
        force_update = True,
        slug = "help_summary_fr",
        language = "fr-fr",
        original = Document.objects.filter(slug = "help"),
        original_field = "summary",
        translated_text = "Twistranet est un réseau social simple mais efficace, "
            "taillé pour l'entreprise. Ce document vous aidera à prendre TwistraNet en main.",
    ),

    Fixture(
        TranslationResource,
        force_update = True,
        slug = "help_text_fr",
        language = "fr-fr",
        original = Document.objects.filter(slug = "help"),
        original_field = "text",
        translated_text = """
        Si vous pouvez lire ce document, c'est que vous êtes déjà connecté à TwistraNet !
        Si vous n'êtes pas déjà identifié, utilisez le lien "me connecter" de cette page pour entrer vos identifiants.
        
        Vous pouvez commencer à travailler avec TwistraNet !
        """,
    ),
]
