"""
Permission mapping by type
TODO: Disallow permission change! Secure this!!!
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from twistranet.lib import roles
from twistranet.lib import permissions
from account import Account
from content import Content


def _applyPermissionsTemplate(target, mapping_class):
    """
    Apply / Re-apply a permissions template
    XXX TODO: More error checking
    XXX TODO: Factorize this into the manager (and securize the manager BTW)
    """
    # Do not apply on base classes
    # if target.__class__ in mapping_class.dont_apply_on:
    #     # Try to get the target object
    #     target = target.object
    #     return _applyPermissionsTemplate(target, mapping_class)
    
    # Get template
    tpl = [ t for t in target.permission_templates.permissions() if t["id"] == target.permissions ]
    if not tpl:
        raise ValidationError("Permissions template '%s' doesn't exist in %s." % (
            target.permissions,
            target.permission_templates.permissions(),
        ))
        
    # Wow, may be a little be excessively optimistic?
    mapping_class.objects.filter(target = target).delete()  # XXX Replace with SQL?
    for perm, roles in tpl[0].items():
        if not perm.startswith("can_"):
            continue
        for role in roles:
            m = mapping_class.objects.create(
                target = target,
                name = perm,
                role = role.value,
                )
            m.save()
    
class _BasePermissionMapping(models.Model):
    """
    model_type => object_id => permission => role
    """
    
    class Meta:
        abstract = True
        
    # Don't forget to define your content type and content foreign key in subclasses
    name = models.CharField(max_length = 32)
    role = models.IntegerField()
    
    def __unicode__(self):
        # Meant to be called on subclasses only (where 'target' is defined)
        return "%s %s '%s'" % (self.role, self.name, self.target, )

class _ContentPermissionMapping(_BasePermissionMapping):
    """
    Permission for content types
    """
    class Meta:
        app_label = "twistranet"
    target = models.ForeignKey(Content, related_name = "_permissions")
    dont_apply_on = (Content, )

    
class _AccountPermissionMapping(_BasePermissionMapping):
    """
    Permission for accounts
    """
    class Meta:
        app_label = "twistranet"
    target = models.ForeignKey(Account, related_name = "_permissions")
    dont_apply_on = (Account, )


