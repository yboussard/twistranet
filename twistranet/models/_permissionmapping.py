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
    # def get_query_set(self):
    #     """
    #     Prohibit queryset usage. Return an empty and dummy filter.
    #     """
    #     return super(_PermissionMappingManager, self).get_query_set().none()
    #     # raise SuspiciousOperation("One should never call this part of the code!")

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

    def _applyPermissionsTemplate(self, target):
        """
        Apply / Re-apply a permissions template.
        
        target is the objects perms will be applied on.
        XXX TODO: More error checking
        XXX TODO: Make it far more efficient ; maybe replace perm names by ids to speed things up
        """
        # Get permissions for actual model class.
        # XXX TODO: Make this more efficient and less 'magic'!
        # XXX For example, move this code into Content and Account as a 'model_class' attribute?
        permission_templates = None
        klasses = (Content, Account)
        for k in klasses:
            if isinstance(target, k):
                t = getattr(target, 'object_type', None)
                if not t:
                    raise ValueError("You can't apply permissions before setting your object_type")
                if t == target.__class__.__name__:
                    permission_templates = target.__class__.permission_templates
                    break
                for sub in target.__class__.__subclasses__():
                    if sub.__name__ == t:
                        permission_templates = sub.permission_templates
                        break
        if not permission_templates:
            raise ValueError("Can't find permission templates for %s" % target.__class__)
        
        # Get template
        tpl = [ t for t in permission_templates.permissions() if t["id"] == target.permissions ]
        if not tpl:
            raise ValidationError("Permissions template '%s' for object '%s' doesn't exist in %s." % (
                target.permissions,
                target,
                [ t['id'] for t in permission_templates.permissions() ],
            ))
        
        # Wow, may be a little be excessively optimistic?
        # Anyway... we use the base query set to bypass security on this.
        super(_PermissionMappingManager, self).get_query_set().filter(target = target).delete()
        for perm, roles in tpl[0].items():
            if not perm.startswith("can_"):
                continue
            # print "add roles %s/%s" % (perm, roles)
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
    _objects = models.Manager()
        
    # Don't forget to define your content type and content foreign key in subclasses
    name = models.CharField(max_length = 32, db_index = True)
    role = models.IntegerField(db_index = True)
    
    def __unicode__(self):
        # Meant to be called on subclasses only (where 'target' is defined)
        return "%s %s '%s'" % (self.role, self.name, self.target, )

class _ContentPermissionMapping(_BasePermissionMapping):
    """
    Permission for content types
    """
    class Meta:
        app_label = "twistranet"
        unique_together = ('target', 'name', 'role', )
        
    target = models.ForeignKey(Content, related_name = "_permissions")
    dont_apply_on = (Content, )

    
class _AccountPermissionMapping(_BasePermissionMapping):
    """
    Permission for accounts
    """
    class Meta:
        app_label = "twistranet"
        unique_together = ('target', 'name', 'role', )

    target = models.ForeignKey(Account, related_name = "_permissions")
    dont_apply_on = (Account, )


