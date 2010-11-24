from django import forms
from django.db import models
from django.forms.widgets import Select, Widget
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe

__all__ = ('PermissionsWidget',)

N_DISPLAYED_ITEMS = 25         # Number of images to display in the inline field

class MediaResourceWidget(Widget):
    """
    This is a powerful widget used to handle media resources.
    One can either select one of its available resources,
    or upload a new file on-the-fly.
    
    Several cases here:
    - If there are less than, say, 25 available media resources,
        just display them without further question.
    - If there are more, display a bit less but provide a little
        search form to find the other ones.
    - In any case, display a form upload widget.
    """
    needs_multipart_form = True
    
    def render(self, name, value, attrs=None):
        """
        Returns this Widget rendered as HTML, as a Unicode string.

        The 'value' given is not guaranteed to be valid input, so subclass
        implementations should program defensively.
        """
        from twistranet.models.resource import Resource
        images = Resource.objects.query_images()[:25]
        if len(images) >= N_DISPLAYED_ITEMS:
            raise NotImplementedError("Should implement image searching & so on")
        ret = u"""
            <div class="mediaresource-widget">
                <div class="mediaresource-help">Select a picture:</div>
            """
        for image in images:
            param_dict = {
                "thumbnail_src": image.get_absolute_url(),
            }
            ret += u"""
            <img src="%(thumbnail_src)s" width="25" height="25"
            >
            """ % param_dict
        ret += u"""
            <div class="mediaresource-help">Or upload a file:</div>
            </div>
            """
        # Return the computed string
        return mark_safe(ret)
    
    

class PermissionsWidget(Select):
    def __init__(self, attrs=None):
        super(Select, self).__init__(attrs)
        self.choices = ()

    def render(self, name, value, attrs=None, ):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select%s>' % flatatt(final_attrs)]
        options = self.render_options([value])
        if options:
            output.append(options)
        output.append(u'</select>')
        return mark_safe(u'\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        return u'<option value="%s"%s>%s</option>' % (
            escape(option_value), selected_html,
            conditional_escape(force_unicode(option_label)))

    def render_options(self, selected_choices):
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in self.choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)
