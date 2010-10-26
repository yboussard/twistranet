import datetime
from haystack.indexes import *
from haystack import site
from twistranet.models import *


class StatusUpdateIndex(SearchIndex):
    searchable_text = CharField(document=True, use_template=True)
    author = CharField(model_attr='author')
    created_at = DateTimeField(model_attr='created_at')

site.register(StatusUpdate, StatusUpdateIndex)


class AccountIndex(SearchIndex):
    searchable_text = CharField(document=True, use_template=True)

site.register(Account, AccountIndex)



