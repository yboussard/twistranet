from base_forms import BaseInlineForm, BaseRegularForm
from django.db import models
from django.forms import widgets

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
        fields = BaseRegularForm.Meta.fields
        widgets = BaseRegularForm.Meta.widgets

