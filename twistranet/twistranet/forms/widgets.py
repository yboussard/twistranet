import os

from django import forms
from django.db import models
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from sorl.thumbnail import default

from twistranet.twistranet.lib.log import log

N_DISPLAYED_ITEMS = 30         # Number of images to display in the inline field


class ResourceWidget(forms.MultiWidget):
    query_set = None
    
    class Media:
        css = {
            'all': ('/static/css/tn_resource_widget.css',),
        }
        js = ('/static/js/tn_resource_widget.js',)

    def __init__(self, initial = None, **kwargs):
        widgets = []
        self.allow_select = kwargs.pop("allow_select", True)
        widgets.append(forms.HiddenInput())
        self.allow_upload = kwargs.pop("allow_upload", True)
        if self.allow_upload:
            widgets.append(forms.FileInput())
        else:
            widgets.append(forms.HiddenInput())
        super(ResourceWidget, self).__init__(widgets)

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
        from twistranet.twistranet.models import Resource, Twistable
        
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
        
        # Render the current resource widget
        if value[0]:
            try:
                img = Resource.objects.get(id = value[0])
            except Resource.DoesNotExist:
                raise       # XXX TODO: Handle the case of a deleted resource
            thumb = default.backend.get_thumbnail( img.object.image, u'100x100' )
            output.append(u"""<div class="mediaresource-help">""" + _(u"Current:") + u"""</div>""")
            param_dict = {
                "thumbnail_src":    thumb.url,
                "value":            img.id,
            }
            output.append(u"""<img src="%(thumbnail_src)s" class="resource-image"
             width="100" height="100" />
             """ % param_dict)
            
        # Render the File widget and the hidden resource ForeignKey
        if self.allow_upload:
            output.append(u"""<div class="mediaresource-help">""" + _(u"Upload a file:") + u"""</div>""")
            for i, widget in enumerate(self.widgets):
                try:
                    widget_value = value[i]
                except IndexError:
                    widget_value = None
                if id_:
                    final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
                output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
            
        # By now we just display resources from our own account.
        # Tomorrow, we should display some kind of album browser.
        if self.allow_select: 
            account = Twistable.objects._getAuthenticatedAccount()
            selectable_accounts = Resource.objects.selectable_accounts(account)
            output.append( '<input type="hidden" id="selector_target" name="selector_target" value="id_%s_0" />' %name )
            # first we display the scopes to select resources (each selectable account)
            output.append( """<div id="resourcepane-main" class="resourcePane">""")
            output.append(u"""<div class="mediaresource-help">""" + _(u"Select an account:") + u"""</div>""")
            output.append( u"""<div class="tnGrid tngridcols-6x">""")
            for scope in selectable_accounts :
                img = scope.forced_picture
                thumb = default.backend.get_thumbnail( img.image,  u'50x50' )
                param_dict = {
                    "url":    scope.get_absolute_url(),
                    "thumbnail_url":    thumb.url,
                    "title":            scope.title,
                    "value":            scope.id,
                }
                output.append(u"""
                  <div class="tnGridItem">
                    <div class="thumbnail-account-part thumbnail-50-bottom">
                      <a href="%(url)s"      
                         title="%(title)s"
                         class="image-block image-block-tile">
                        <img src="%(thumbnail_url)s" 
                             alt="%(title)s" />
                      </a>
                      <label>
                        <a href="%(url)s">%(title)s</a>
                      </label>    
                    </div>    
                    <input type="hidden"
                           name="scope-input"
                           class="scope-input"
                           value="%(value)s" />
                  </div>""" % param_dict)
            output.append( """</div>""")
            output.append( """</div>""")
            
            for scope in selectable_accounts :
                # Pane with objects in each selected account              
                images = Resource.objects.filter(publisher=scope)[:N_DISPLAYED_ITEMS]
                output.append( u"""<div id="resourcepane-%s" class="resourcePane">""" %scope.id)
                if images :
                    output.append(u"""<div class="mediaresource-help">""" + _(u"Select a picture:") + u"""</div>""")
                else :
                    output.append(u"""<div class="mediaresource-help">""" + _(u"No picture available in this account") + u"""</div>""")
                output.append( u"""<div class="tnGrid tngridcols-6x">""")
                if len(images) >= N_DISPLAYED_ITEMS:
                    raise NotImplementedError("Should implement image searching & so on")
                for img in images:
                    thumb = default.backend.get_thumbnail( img.object.image, u'50x50' )
                    is_selected = img.id == int(value[0] or 0)
                    param_dict = {
                        "fullimage_url":    img.get_absolute_url(),
                        "thumbnail_url":    thumb.url,
                        "value":            img.id,          
                        "title":            img.title,
                        "selected":    is_selected and ' checked="checked"' or '',
                    }
                    output.append(u"""
                      <div class="tnGridItem">
                        <div class="thumbnail-account-part thumbnail-50-bottom">
                          <a href="%(fullimage_url)s"      
                             title="%(title)s"
                             class="image-block image-block-tile">
                            <img src="%(thumbnail_url)s" 
                                 alt="%(title)s" />
                          </a>
                          <label>
                            <a href="%(fullimage_url)s">%(title)s</a>
                          </label>
                        </div>
                        <input type="radio"
                               name="grid-item-input"
                               class="grid-item-input"
                               value="%(value)s"
                               %(selected)s />
                      </div>""" % param_dict)
                      
                output.append("""</div>""") # (close the tnGrid div)
                output.append("""</div>""") # (close the resourcepane div)
        
        # finalize and return the complete resource widget
        
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
        options = self.render_options([value])
        if options:
            output.append(options)
        output.append(u'</select>')
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
        for option_value, option_label in self.choices:
            output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)
