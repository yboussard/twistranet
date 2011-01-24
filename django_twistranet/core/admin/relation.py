from django_twistranet.models import Relation
from django.contrib import admin       

class InitiatorInline(admin.StackedInline):
    model = Relation
    extra = 1
    fk_name = "initiator"

class TargetInline(admin.StackedInline):
    model = Relation
    extra = 1
    fk_name = "target"

admin.site.register(Relation)
