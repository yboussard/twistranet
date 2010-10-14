"""
The language system in TwistraNet

Bascially, a content OR a resource _can_ have a language set.
A user _must_ have a list of prefered languages.

Content will be then displayed in user's prefered language.
Content in other languages is still displayable, but no primarily.
"""

import settings

# Add the international lng to the list of available languages
available_languages = (("", 'None', ), ) + settings.LANGUAGES

