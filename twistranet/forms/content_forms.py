from base_forms import BaseInlineForm, BaseRegularForm
from django.db import models
from django.forms import widgets
from twistranet.lib import form_registry

class StatusUpdateForm(BaseInlineForm):
    """
    The famous status update.
    """
    class Meta(BaseInlineForm.Meta):
        from twistranet.models.content_types import StatusUpdate
        model = StatusUpdate
        fields = BaseInlineForm.Meta.fields
        widgets = BaseInlineForm.Meta.widgets

class DocumentForm(BaseRegularForm):
    """
    A full-featured document form
    """
    class Meta(BaseRegularForm.Meta):
        from twistranet.models.content_types import Document
        model = Document
        fields = ('title', ) + BaseRegularForm.Meta.fields + ('resources', )
        widgets = BaseRegularForm.Meta.widgets

form_registry.register(StatusUpdateForm)
form_registry.register(DocumentForm)
