import os
import traceback
import mimetypes
from django import forms
from django.db import models
from django.conf import settings
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from sorl.thumbnail import default
from django.template import loader, Context

from twistranet.twistapp.lib.log import log

N_DISPLAYED_ITEMS = 30         # Number of images to display in the inline field


class ResourceWidget(forms.MultiWidget):
    query_set = None

    def _media(self):
        base_url = settings.MEDIA_URL
        while base_url.endswith('/'):
            base_url = base_url[:-1]
        return forms.Media(
            css = {
                'all': ('%s/static/css/tn_resource_widget.css' % base_url, ),
            },
            js = ('%s/static/js/tn_resource_widget.js' % base_url, )
        )
    media = property(_media)

    def __init__(self, initial = None, **kwargs):
        widgets = []
        widgets.append(forms.HiddenInput())
        super(ResourceWidget, self).__init__(widgets)
        self.display_renderer = kwargs.pop("display_renderer", True)
        self.allow_select = kwargs.pop("allow_select", True)
        self.allow_upload = kwargs.pop("allow_upload", True)
        self.media_type = kwargs.pop("media_type", 'image')

    def decompress(self, value):
        """
        Handle choices generation for the reference widget.
        """
        return (value, None)


    def render(self, name, value, attrs=None):
        """
        Returns this Widget rendered as HTML, as a Unicode string.

        The 'value' given is just the resource number or None if not given.

        Basically, this widget has 3 zones:

        - The current resource, if there is already one.
        - The file upload field
        - The resource browser.
        """            
        from twistranet.twistapp.models import Resource, Twistable

        # Beginning of the super-render() code
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        output.append(u"""<div class="resource-widget">""")
        
        # Render the current resource widget and the room for preview
        if self.display_renderer or value[0]:
            output.append( """<div id="resources-renderer">""" )
            if value[0]:
                output.append("""<div id="renderer-current" class="renderer-preview">""")
                try:
                    resource = Resource.objects.get(id = value[0])
                except Resource.DoesNotExist:
                    raise       # XXX TODO: Handle the case of a deleted resource
                thumb = resource.thumbnails['summary_preview']
                output.append(u"""<div class="mediaresource-help">""" + _(u"Current:") + u"""</div>""")
                param_dict = {
                    "thumbnail_url":    thumb.url,
                    "value":            resource.id,
                    "title":            resource.title,
                    "res_url":          resource.get_absolute_url(),
                }
                output.append(u"""
                  <a class="image-block"
                     title="%(title)s"
                     href="%(res_url)s">
                      <img src="%(thumbnail_url)s"
                           alt="%(title)s"
                           id="resource-current" />
                     <span class="image-block-legend">%(title)s</span>
                   </a>
                 """ % param_dict)

                output.append( """</div>""" ) # close renderer-current div

            output.append("""<div id="renderer-new" class="renderer-preview">""")
            output.append("""<div class="mediaresource-help">""" + _(u"Uploaded file:") + """</div></div>""")

            output.append( """</div>""" ) # close resources-renderer div

        # Render computed widgets
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))

        # Render hidden fields used for upload and browser
        output.append('<input type="hidden" name="media_type" value="%s" />' %self.media_type)
        output.append('<input type="hidden" name="selector_target" value="id_%s_0" />' %name)
        
        # Render the Quick upload File widget
        if self.allow_upload:
            output.append('<div class="tnQuickUpload"></div>')

        # Display browser resources in all selectable accounts
        if self.allow_select:
            auth = Twistable.objects._getAuthenticatedAccount()
            default_publisher = getattr(self, 'publisher', None)
            if default_publisher is None:
                default_publisher = auth
            selectable_accounts = Resource.objects.selectable_accounts(auth)
            sids = [s.id for s in selectable_accounts]
            if default_publisher.id and default_publisher.id not in sids:
                selectable_accounts.insert(0, default_publisher)
            t = loader.get_template('resource/resource_browser.html')
            scopes = []
            for account in selectable_accounts:
                img = account.forced_picture
                icon = img.thumbnails['icon']
                activeClass = account.id == default_publisher.id and ' activePane' or ''
                scope = {
                    "url":              account.get_absolute_url(),
                    "icon_url":         icon.url,
                    "title":            account.title,
                    "id":               account.id,
                    "activeClass":      activeClass,
                }
                scope['icons'] = []
                # XXX TODO (JMG) : use haystack for search only resource with is_image=1
                images = Resource.objects.filter(publisher=account)
                for img in images:
                    if len(scope['icons'])<=9:
                        icon = img.thumbnails['icon']
                        scope['icons'].append(icon.url)
                scopes.append(scope)

            c = Context({
                'name': name, 
                'scopes': scopes,
                'publisher_id': self.publisher_id,      # Default publisher id
            })
            output.append (t.render(c))

        # finalize and return the complete resource widget
        output.append("""<div class="clear"><!-- --></div>""")
        output.append("""</div>""") # (close the resource-widget div)

        return mark_safe(self.format_output(output))



class PermissionsWidget(forms.Select):

    def __init__(self, attrs=None, choices=()):
        super(PermissionsWidget, self).__init__(attrs, choices)
        default_attrs = {'class': 'permissions-widget'}
        if attrs:
            default_attrs.update(attrs)
        # remove id (possible js conflict in inline forms) > TODO : improve in inline forms
        default_attrs['id']=''
        self.attrs = default_attrs

    def render(self, name, value, attrs=None, ):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select%s>' % flatatt(final_attrs)]
        render_options = self.render_options([value])
        options = render_options[0]
        descriptions = render_options[1]
        if options:
            output.append(options)
        output.append(u'</select>')
        for d in descriptions:
            output.append('<span class="hint">%s</span>' %d)
        return mark_safe(u'\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        return u'<option class="%s" value="%s"%s>%s</option>' % (
            escape(option_value), escape(option_value), selected_html,
            conditional_escape(force_unicode(option_label)))

    def render_options(self, selected_choices):
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        descriptions = []
        for option_value, option_label, option_description in self.choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
            descriptions.append(option_description)
        return u'\n'.join(output), descriptions