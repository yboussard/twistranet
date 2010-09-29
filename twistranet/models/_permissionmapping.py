"""
Permission mapping by type
TODO: Disallow permission change! Secure this!!!
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, SuspiciousOperation
from twistranet.lib import roles
from twistranet.lib import permissions
from account import Account
from content import Content
from basemanager import BaseManager

class _PermissionMappingManager(BaseManager):
    """
    Ensure that security is applied: we can't manipulate unauthorized objects.
    """
    def get_query_set(self):
        """
        Prohibit queryset usage. Return an empty and dummy filter.
        """
        return super(_PermissionMappingManager, self).get_query_set().filter(name = None)
        # raise SuspiciousOperation("One should never call this part of the code!")

    def _get_detail(self, object_id):
        """
        Return a detailed permission set as a dict for object id
        """
        ret = {}
        for p in super(_PermissionMappingManager, self).get_query_set().filter(target = object_id):
            if ret.has_key(p.name):
                ret[p.name].append(p.role)
            else:
                ret[p.name] = [p.role]
        return ret

    def _applyPermissionsTemplate(self, target, mapping_class):
        """
        Apply / Re-apply a permissions template
        XXX TODO: More error checking
        """
        # Get permissions for actual model class
        target_class = target.model_class
        
        # Get template
        tpl = [ t for t in target_class.permission_templates.permissions() if t["id"] == target.permissions ]
        if not tpl:
            raise ValidationError("Permissions template '%s' for object '%s' doesn't exist in %s." % (
                target.permissions,
                target,
                [ t['id'] for t in target_class.permission_templates.permissions() ],
            ))
        
        # Wow, may be a little be excessively optimistic?
        # Anyway... we use the base query set to bypass security on this.
        super(_PermissionMappingManager, self).get_query_set().filter(target = target).delete()
        for perm, roles in tpl[0].items():
            if not perm.startswith("can_"):
                continue
            for role in roles:
                m = self.create(
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
        
    # The objects overloading
    objects = _PermissionMappingManager()
        
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


