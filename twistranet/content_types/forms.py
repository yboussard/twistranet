from django.db import models
from django.forms import widgets

from tinymce.widgets import TinyMCE

from twistranet.twistranet.forms import form_registry
from twistranet.twistranet.forms.base_forms import BaseInlineForm, BaseRegularForm

class StatusUpdateForm(BaseInlineForm):
    """
    The famous status update.
    """
    icon = "statusupdate.png"
    
    class Meta(BaseInlineForm.Meta):
        from twistranet.content_types.models import StatusUpdate
        model = StatusUpdate
        fields = BaseInlineForm.Meta.fields
        widgets = BaseInlineForm.Meta.widgets

class QuickDocumentForm(BaseRegularForm):
    """
    A quick-entry document form.
    We just have a pretty "text" field, which will distribute its values amongst title, description and actual text field.
    This is for creation only.
    """
    allow_creation = True
    allow_edition = False
    icon = "document.png"
    
    class Meta(BaseRegularForm.Meta):
        from twistranet.content_types.models import Document
        model = Document
        fields = ('title', 'description', 'resources', ) + BaseRegularForm.Meta.fields
        widgets = {
            'description':  widgets.Textarea(attrs = {'rows': 3, 'cols': 60}),
            'text':         TinyMCE(attrs = {'rows': 20, 'cols': 100}),
        }

class DocumentForm(BaseRegularForm):
    """
    A full-featured document form, used for edition only
    """
    allow_creation = False
    allow_edition = True
    icon = "document.png"

    class Meta(BaseRegularForm.Meta):
        from twistranet.content_types.models import Document
        model = Document
        fields = ('title', 'description', ) + BaseRegularForm.Meta.fields
        widgets = {
            'description':  widgets.Textarea(attrs = {'rows': 3, 'cols': 60}),
            'text':         TinyMCE(attrs = {'rows': 30, 'cols': 120}),
        }

form_registry.register(StatusUpdateForm)
form_registry.register(QuickDocumentForm)
form_registry.register(DocumentForm)



