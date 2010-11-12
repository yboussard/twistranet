# -*- coding: utf-8 -*-
from twistrans.lib import TranslationFixture

FIXTURES = [
    TranslationFixture(
        language = "fr-fr",
        original_slug = "all_twistranet",
        original_field = "screen_name",
        translated_text = "Tous les membres",
    ),

    TranslationFixture(
        original_slug = "menuitem_home",
        language = "fr-fr",
        original_field = "title",
        translated_text = "Accueil",
    ),

    TranslationFixture(
        original_slug = "menuitem_communities",
        language = "fr-fr",
        original_field = "title",
        translated_text = "Communautés",
    ),
    
    TranslationFixture(
        original_slug = "menuitem_all_communities",
        language = "fr-fr",
        original_field = "title",
        translated_text = "Toutes les communautés",
    ),
    
    TranslationFixture(
        original_slug = "administrators",
        language = "fr-fr",
        original_field = "screen_name",
        translated_text = "Les administrateurs",
    ),
]