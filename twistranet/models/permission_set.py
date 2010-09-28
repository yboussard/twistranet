"""
Permission types and default permission sets.
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from twistranet.lib import roles
from twistranet.lib.permissions import *
from account import Account
from content import Content

class PermissionSet(models.Model):
    """
    A permission definition.
    """
    name = models.CharField(max_length = 32)
    description = models.TextField()
    object_type = models.CharField(max_length = 32)
    weight = models.IntegerField()    # Used to sort. Higher weight = lower in the list
    
    
class PermissionSetting(models.Model):
    """
    Association between a permission set and a permission role.
    Not meant to be edited.
    """
    permission_set = models.ForeignKey(PermissionSet)
    permission_name = models.CharField(max_length = 32)
    permission_role = models.IntegerField()

