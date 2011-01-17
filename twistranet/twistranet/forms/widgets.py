import os

from django import forms
from django.db import models
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from sorl.thumbnail import default
from django.template import loader, Context
from django.conf import settings

from twistranet.twistranet.lib.log import log

N_DISPLAYED_ITEMS = 30         # Number of images to display in the inline field

QUICK_UPLOAD_JS = """       
    var fillTitles = %(ul_fill_titles)s;
    var auto = %(ul_auto_upload)s;
    addUploadFields_%(ul_id)s = function(file, id) {
        var uploader = xhr_%(ul_id)s;
        TwistranetQuickUpload.addUploadFields(uploader, uploader._element, file, id, fillTitles);
    }
    sendDataAndUpload_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        TwistranetQuickUpload.sendDataAndUpload(uploader, uploader._element, '%(typeupload)s');
    }    
    clearQueue_%(ul_id)s = function() {
        var uploader = xhr_%(ul_id)s;
        TwistranetQuickUpload.clearQueue(uploader, uploader._element);    
    }    
    onUploadComplete_%(ul_id)s = function(id, fileName, responseJSON) {       
        var uploader = xhr_%(ul_id)s;
        TwistranetQuickUpload.onUploadComplete(uploader, uploader._element, id, fileName, responseJSON);
    }
    createUploader_%(ul_id)s= function(){    
        xhr_%(ul_id)s = new qq.FileUploader({
            element: jQuery('#%(ul_id)s')[0],
            action: '/resource_quickupload',
            autoUpload: auto,
            onAfterSelect: addUploadFields_%(ul_id)s,
            onComplete: onUploadComplete_%(ul_id)s,
            allowedExtensions: %(ul_file_extensions_list)s,
            sizeLimit: %(ul_xhr_size_limit)s,
            simUploadLimit: %(ul_sim_upload_limit)s,
            template: '<div class="qq-uploader">' +
                      '<div class="qq-upload-drop-area"><span>%(ul_draganddrop_text)s</span></div>' +
                      '<div class="qq-upload-button">%(ul_button_text)s</div>' +
                      '<ul class="qq-upload-list"></ul>' + 
                      '</div>',
            fileTemplate: '<li>' +
                    '<a class="qq-upload-cancel" href="#">&nbsp;</a>' +
                    '<div class="qq-upload-infos"><span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-failed-text">%(ul_msg_failed)s</span></div>' +
                    '<div class="qq-upload-size"></div>' +
                '</li>',                      
            messages: {
                serverError: "%(ul_error_server)s",
                typeError: "%(ul_error_bad_ext)s {file}. %(ul_error_onlyallowed)s {extensions}.",
                sizeError: "%(ul_error_file_large)s {file}, %(ul_error_maxsize_is)s {sizeLimit}.",
                emptyError: "%(ul_error_empty_file)s {file}, %(ul_error_try_again_wo)s"
            }            
        });           
    }
    jQuery(document).ready(createUploader_%(ul_id)s); 
"""


class ResourceWidget(forms.MultiWidget):
    query_set = None

    class Media:
        css = {
            'all': ('/static/css/fileuploader.css', '/static/css/tn_resource_widget.css', ),
        }
        js = ('/static/js/fileuploader.js', '/static/js/tn_resource_widget.js', )

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
            output.append( """<div id="resources-renderer">""" )
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

            output.append( """</div>""" ) # close resources-renderer div

        # Render the File widget and the hidden resource ForeignKey
        if self.allow_upload and not self.allow_select :
            output.append( """<div id="resources-uploader">""" )
            output.append(u"""<div class="mediaresource-help">""" + _(u"Upload a file:") + u"""</div>""")
            for i, widget in enumerate(self.widgets):
                try:
                    widget_value = value[i]
                except IndexError:
                    widget_value = None
                if id_:
                    final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
                output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
            output.append( """</div>""" ) # close resources-uploader div

        # Display resources from all selectable accounts.
        if self.allow_select:
            account = Twistable.objects._getAuthenticatedAccount()
            selectable_accounts = Resource.objects.selectable_accounts(account)
            
            
            t = loader.get_template('resource/resource_browser.html')
            scopes = []
            for account in selectable_accounts :
                img = account.forced_picture
                icon = default.backend.get_thumbnail( img.image,  u'16x16' )
                scope = {
                    "url":              account.get_absolute_url(),
                    "icon_url":         icon.url,
                    "title":            account.title,
                    "id":               account.id, 
                }
                scope['images'] = []
                scope['icons'] = []
                images = Resource.objects.filter(publisher=account)[:N_DISPLAYED_ITEMS]
                if len(images) >= N_DISPLAYED_ITEMS:
                    raise NotImplementedError("Should implement image searching & so on")
                for img in images :
                    thumb = default.backend.get_thumbnail( img.object.image, u'50x50' )
                    is_selected = img.id == int(value[0] or 0)
                    image = {
                            "url":              img.get_absolute_url(),
                            "thumbnail_url":    thumb.url,
                            "id":               img.id,
                            "title":            img.title,
                            "selected":         is_selected and ' checked="checked"' or ''
                            }
                    scope['images'].append(image)
                    if len(scope['icons'])<=9 :               
                        icon = default.backend.get_thumbnail( img.object.image, u'16x16' )
                        scope['icons'].append(icon.url)
                scopes.append(scope)

            c = Context({ 'name': name, 'scopes' : scopes, })     
            
            if self.allow_upload :
                
                qu_settings = dict(
                    typeupload             = 'File',
                    ul_id                  = 'tnuploader', # improve it to get multiple uploader in a same page, change it also in 'resource_quickupload.html'
                    ul_file_extensions_list = '[]', #could be ['jpg,'png','gif']
                    
                    ul_fill_titles         = settings.QUICKUPLOAD_FILL_TITLES and 'true' or 'false',
                    ul_auto_upload         = settings.QUICKUPLOAD_AUTO_UPLOAD and 'true' or 'false',
                    ul_xhr_size_limit      = settings.QUICKUPLOAD_SIZE_LIMIT and str(settings.QUICKUPLOAD_SIZE_LIMIT*1024) or '0',
                    ul_sim_upload_limit    = str(settings.QUICKUPLOAD_SIM_UPLOAD_LIMIT),
                    ul_button_text         = _(u'Browse'),
                    ul_draganddrop_text    = _(u'Drag and drop files to upload'),
                    ul_msg_all_sucess      = _( u'All files uploaded with success.'),
                    ul_msg_some_sucess     = _( u' files uploaded with success, '),
                    ul_msg_some_errors     = _( u" uploads return an error."),
                    ul_msg_failed          = _( u"Failed"),
                    ul_error_try_again_wo  = _( u"please select files again without it."),
                    ul_error_try_again     = _( u"please try again."),
                    ul_error_empty_file    = _( u"This file is empty :"),
                    ul_error_file_large    = _( u"This file is too large :"),
                    ul_error_maxsize_is    = _( u"maximum file size is :"),
                    ul_error_bad_ext       = _( u"This file has invalid extension :"),
                    ul_error_onlyallowed   = _( u"Only allowed :"),
                    ul_error_server        = _( u"Server error, please contact support and/or try again."),
                )
                qu_script = QUICK_UPLOAD_JS % qu_settings
                uc = Context({ 'qu_script': qu_script, }) 
                upload_template = loader.get_template('resource/resource_quickupload.html')
                output.append (upload_template.render(uc))
            
            output.append (t.render(c))

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