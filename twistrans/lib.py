"""
Content translation helper.
This is a wrapper around a real content object which provides some helpful methods.
"""
from twistrans.models import TranslationResource

class _TranslationWrapper(object):
    """
    This encapsulates the translation behavior of a content.
    It allows the content.translation.field syntax.
    
    It also simulates part of the save() behavior 
    by creating/updating the xxx_headline and xxx_summary fields.
    """
    def __init__(self, content, language):
        """
        Ok let's go
        """
        self._content = content
        self._language = language
        self._translations = {}
        for trans in content._field_translations.values("language", "original_field", "translation"):
            # We do this to ensure that for eg. 'fr-fr' will always match 'fr'
            if trans['language'][:2] == language[:2]:
                if self._translations.has_key(trans['original_field']):
                    if trans['language'][3:] <> language[3:]:
                        continue    # We have another match
                self._translations[trans['original_field']] = trans['translation']

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
            return getattr(self._content, attr)

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
        args = []
        for f in self._content._meta.fields:
            args.append(getattr(self, f.name))
        translated_copy = self._content.__class__(*args)
        translated_copy.save = None                           # We prevent saving by removing the save() method.
                                                            # Ok, it's not perfect, but it should work.
        
        # Call the generation methods and create Resource objects for each
        for field, method in translated_copy.auto_values:
            meth = getattr(translated_copy, method)
            setattr(translated_copy, field, meth())
            
        # We loop twice to ensure a proper order (is it really necessary? not sure...)
        for field, method in self._content.auto_values:
            r = TranslationResource.objects.filter(
                locator = "translation/%i/%s/%s" % (self._content.id, field, self._language, )
                )
            if r:
                resource = r.get()
            else:
                resource = TranslationResource(
                    language = self._language,
                    original_field = field,
                    original_content = self._content,
                    locator = "translation/%i/%s/%s" % (self._content.id, field, self._language, ),
                    )
            resource.translation = getattr(translated_copy, field)
            resource.save()
            
        # Ok, done!

