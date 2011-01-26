"""
The menu / taxonomy system for TwistraNet.

This is directly inspired from http://code.google.com/p/django-menu/

XXX TODO: Make this translatable
"""
from django.db import models
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation
from twistranet.twistapp.models import Twistable, Content, Account
from twistranet.twistapp.lib import permissions

 
class MenuItem(Twistable):
    """
    A menu can point either to a view, an internal or external URL or a Twistable object.
    In the latter case, the menu label is determine by the Twistable's title.
    """
    # Not very efficient ordering property
    order = models.IntegerField(default = 0)

    # Target URL / Object / Permissions
    url_name = models.CharField(max_length=100, help_text='URL Name for Reverse Lookup, eg comments.comment_was_posted', blank=True, null=True, )
    view_path = models.CharField(max_length=100, help_text='Python Path to View to Render, eg django.contrib.admin.views.main.index', blank=True, null=True, )
    link_url = models.CharField(max_length=100, help_text='URL or URI to the content, eg /about/ or http://foo.com/', blank=True, null=True, )
    target = models.ForeignKey("Twistable", related_name = "menu_items", null = True, blank = True)
    
    # Parenting stuff
    parent = models.ForeignKey('MenuItem', related_name = '_children', null = True, blank = True)

    permission_templates = permissions.content_templates        # This is the lazy man's solution, we use same perms as content ;)
    default_picture_resource_slug = "default_menu_picture"
    
    class Meta:
        app_label = 'twistapp'
         
    def save(self, *args, **kw):
        """
        Ensure DB consistancy
        """
        # Check that we're not trying to set a parent on a pure Menu object
        if isinstance(self, Menu):
            if self.parent or self.parent_id:
                raise ValidationError("A Menu must not have a parent.")
        else:
            if not self.parent_id and not self.parent:
                raise ValidationError("A MenuItem must have a parent.")
        
        # Check if there's at least one access method and dereference target if needed.
        if self.target:
            # If target is set, we set the publisher to the same value.
            # This way, the menu item has the same visibility as its target (if its publisher doesn't change)
            if isinstance(self.target, Account):
                self.publisher = self.target
            else:
                self.publisher = self.target.publisher
        elif (not self.url_name and not self.view_path and not self.link_url):
            if not isinstance(self, Menu):
                raise ValueError("Should have at least one target or path specified for the menu item")
        
        # Call the super
        super(MenuItem, self).save(*args, **kw)
        
    @property
    def has_children(self):
        """
        You can override this if you want in your subclass
        """
        return MenuItem.objects.filter(parent = self).exists()

    @property
    def children(self):
        """
        You can override this, maybe?
        """
        return MenuItem.objects.filter(parent = self).order_by('order')

    @property
    def label(self):
        """
        Use this in your templates instead of title as some pre-processing occurs.
        """
        if self.title:
            return self.title
        
        # We've got a target, return its title
        t = self.target.object
        return t.title
                
        # Uh oh, shouldn't reach there
        raise AssertionError("Shouldn't reach here with MenuItem %s" % self.id)

    def get_absolute_url(self):
        """
        Return absolute URL according to the given information
        """
        # Regular path resolution
        if self.url_name:
            return urlresolvers.reverse(self.url_name)
        elif self.view_path:
            return urlresolvers.reverse(self.view_path)
        elif self.link_url:
            return self.link_url
            
        # No fast shortcut. Got a target id instead?
        return self.target.get_absolute_url()

    

class Menu(MenuItem):
    """
    After all, a menu is just a special kind of menu item.
    """
    class Admin:
        pass

    class Meta:
        app_label = 'twistapp'
        
    def save(self, *args, **kw):
        """
        Re-order all items at from 10 upwards, at intervals of 10.
        This makes it easy to insert new items in the middle of
        existing items without having to manually shuffle
        them all around.
        """
        super(Menu, self).save(*args, **kw)

        current = 10
        for item in self.children:
            item.order = current
            item.save()
            current += 10



    