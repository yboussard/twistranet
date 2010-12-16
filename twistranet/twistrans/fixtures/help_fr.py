# -*- coding: utf-8 -*-
"""
This is used to translate the EN version into FR
"""
from twistranet.twistrans.lib import TranslationFixture

FIXTURES = [
    TranslationFixture(
        language = "fr-fr",
        original_slug = "help",
        original_field = "title",
        translated_text = "Aide de TwistraNet",
    ),
    
    TranslationFixture(
        language = "fr-fr",
        original_slug = "help",
        original_field = "description",
        translated_text = "Twistranet est un réseau social simple mais efficace, "
            "taillé pour l'entreprise. Ce document vous aidera à prendre TwistraNet en main.",
    ),

    TranslationFixture(
        language = "fr-fr",
        original_slug = "help",
        original_field = "text",
        translated_text = """
        Si vous pouvez lire ce document, c'est que vous êtes déjà connecté à TwistraNet !
        Si vous n'êtes pas déjà identifié, utilisez le lien "me connecter" de cette page pour entrer vos identifiants.
        
        Vous pouvez commencer à travailler avec TwistraNet !
        """,
    ),

    TranslationFixture(
        language = "fr-fr",
        original_slug = "menuitem_help",
        original_field = "title",
        translated_text = "Aide",
    ),
]
