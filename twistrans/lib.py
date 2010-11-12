"""
Content translation helper.
This is a wrapper around a real content object which provides some helpful methods.
"""
from twistrans.models import TranslationResource
from twistranet.lib.python_fixture import Fixture

class TranslationFixture(Fixture):
    """
    Helper for translation in fixtures.
    Just provide original_slug, original_field and translated_text, the rest is computed for ya.
    """

    def __init__(self, language, original_slug, original_field, translated_text, force_update = True):
        """
        Compute initial data.
        
        TranslationResource,
        force_update = True,
        slug = "menuitem_home_fr_fr",
        language = "fr-fr",
        original = Twistable.objects.filter(slug = "home"),
        original_field = "title",
        translated_text = "Accueil",
        """
        from twistranet.models import Twistable
        super(TranslationFixture, self).__init__(
            TranslationResource,
            force_update = force_update,
            slug = "%s_%s_%s" % (original_slug, original_field, language.replace("-", "_"), ),
            language = language,
            original = Twistable.objects.filter(slug = original_slug),
            original_field = original_field,
            translated_text = translated_text,
        )
    
    def apply(self,):
        """
        Handle attributes according to initial data
        """
        # Special treatment for translation stuff
        obj = super(TranslationFixture, self).apply()
        obj.original.object._translation(language = obj.language).save()


class _TranslationWrapper(object):
    """
    This encapsulates the translation behavior of a content.
    It allows the content.translation.field syntax.
    
    It also simulates part of the save() behavior 
    by creating/updating the xxx_headline and xxx_summary fields.
    
    XXX TODO: Make this more optimal by reducing the number of calls: the wrapper must be cached!
    """
    def __init__(self, content, language):
        """
        Ok let's go
        """
        self._content = content
        self._language = language
        self._translations = {}
        for trans in content._field_translations.values("language", "original_field", "translated_text"):
            # We do this to ensure that for eg. 'fr-fr' will always match 'fr'
            if trans['language'][:2] == language[:2]:
                if self._translations.has_key(trans['original_field']):
                    if trans['language'][3:] <> language[3:]:
                        continue    # We have another match
                self._translations[trans['original_field']] = trans['translated_text']
        self._fake = self._fake_copy(content)

    def __getattr__(self, attr):
        """
        Return either the translated version of the content if it exists,
        or the international (or default) one if not.
        """
        # if not hasattr(self._content, attr):
        #     raise AttributeError("%s instance has no attribute %s" % (self._content.__class__.__name__, attr))
        try:
            return self._translations[attr]
        except KeyError:
            return getattr(self._fake, attr)
            
    def _fake_copy(self, original):
        """
        Create a fake copy form the original object.
        This creates a 'fake' object still bearing interesting methods.
        Useful for 'auto" fields.
        """
        args = []
        for f in original._meta.fields:
            try:
                v = self._translations[f.name]
            except KeyError:
                v = f.value_from_object(original)
            args.append(v)
        translated_copy = original.__class__(*args)
        translated_copy.save = None                             # We prevent saving by removing the save() method.
                                                                # Ok, it's not perfect, but it should work.
        return translated_copy

    def save(self,):
        """
        Simulate a content saving. Use this to automatically update xxx_headline and xxx_summary translations.
        Of course you need to have the view permission on the content and a translate permission.
        
        XXX TODO: Check permissions
        XXX Warning: Edition is sub-optimal. Should I find sth better for auto attributes?
        """
        # Generate each attribute.
        if self.__class__.__name__ == "Content":
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
        
        # Create a fake content around the translated one
        translated_copy = self._fake_copy(self._content)
        
        # Call the generation methods and create Resource objects for each.
        # twistable.auto_values is a sequence of (field, generator_method) tuples.
        # We call generator_method to populate the field.
        for field, method in getattr(translated_copy, 'auto_values', []):
            meth = getattr(translated_copy, method)
            setattr(translated_copy, field, meth())
            
        # We loop twice to ensure a proper order (is it really necessary? not sure...)
        for field, method in getattr(translated_copy, 'auto_values', []):
            r = TranslationResource.objects.filter(
                locator = "translation/%i/%s/%s" % (self._content.id, field, self._language, )
                )
            if r:
                resource = r.get()
            else:
                resource = TranslationResource(
                    language = self._language,
                    original_field = field,
                    original = self._content,
                    locator = "translation/%i/%s/%s" % (self._content.id, field, self._language, ),
                    )
            resource.translated_text = getattr(translated_copy, field)
            resource.save()
            
        # Ok, done!

