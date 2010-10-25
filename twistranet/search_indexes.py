import datetime
from haystack.indexes import *
from haystack import site
from twistranet.models import *


class StatusUpdateIndex(SearchIndex):
    searchable_text = CharField(document=True, use_template=True)
    # author = CharField(model_attr='user')
    date = DateTimeField(model_attr='date')

    # def get_queryset(self):
    #     """Used when the entire index for model is updated."""
    #     return StatusUpdate.objects


site.register(StatusUpdate, StatusUpdateIndex)

