"""
The menu / taxonomy system for TwistraNet.

This is directly inspired from http://code.google.com/p/django-menu/

XXX TODO: Make this translatable
"""
from django.db import models
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from twistranet.models import Twistable, Content, Account
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation

class _MenuItemContainer(object):
    """
    Used to make the subitem possible on the root Menu object
    """
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
        ret = []
        if isinstance(self, MenuItem):
            for child in self._children.order_by('order'):
                if child.can_view:
                    ret.append(child)
        elif isinstance(self, Menu):
            for child in MenuItem.objects.filter(menu = self.id, parent = None).order_by('order'):
                if child.can_view:
                    ret.append(child)
        else:
            raise AssertionError("Inherits from this class without a reason")
            
        return ret


class Menu(Twistable, _MenuItemContainer):
    class Admin:
        pass
        
    class Meta:
        app_label = "twistranet"
 
    def __unicode__(self):
        return _("%s" % self.slug)
 
    def save(self):
        """
        Re-order all items at from 10 upwards, at intervals of 10.
        This makes it easy to insert new items in the middle of
        existing items without having to manually shuffle
        them all around.
        """
        super(Menu, self).save()
 
        current = 10
        for item in MenuItem.objects.filter(menu=self).order_by('order'):
            item.order = current
            item.save()
            current += 10
 
 
 
class MenuItem(Twistable, _MenuItemContainer):
    """
    A menu can point either to a view, an internal or external URL or a Twistable object.
    In the latter case, the menu label is determine by the Twistable's title.
    """
    menu = models.ForeignKey(Menu)
    order = models.IntegerField()

    # Target URL / Object / Permissions
    url_name = models.CharField(max_length=100, help_text='URL Name for Reverse Lookup, eg comments.comment_was_posted', blank=True, null=True, )
    view_path = models.CharField(max_length=100, help_text='Python Path to View to Render, eg django.contrib.admin.views.main.index', blank=True, null=True, )
    link_url = models.CharField(max_length=100, help_text='URL or URI to the content, eg /about/ or http://foo.com/', blank=True, null=True, )
    target = models.ForeignKey("Twistable", related_name = "menu_items", null = True)
    
    # Parenting stuff
    parent = models.ForeignKey('MenuItem', related_name = '_children', null = True)

    class Meta:
        app_label = "twistranet"
 
    def __unicode__(self):
        return _("%s %s. %s" % (self.menu.slug, self.order, self.title))
        
    def save(self, *args, **kw):
        """
        Ensure DB consistancy
        """
        from twistranet.models import Content, Account
        
        # Check if there's at least one access method and dereference target if needed.
        if hasattr(self, 'target'):
            pass    # Err, in fact, nothing more to do here.
        elif (not self.url_name and not self.view_path and not self.link_url):
            raise ValueError("Should have at least one target or path specified for the menu")
        
        # Call the super
        super(MenuItem, self).save(*args, **kw)

    @property
    def can_view(self):
        """Here, if a target is set, we check if it has can_view permission.
        """
        t = self.target
        if t:
            return t.can_view

        # No target => We can see it anyway (by now)
        # XXX TODO: Implement a better security model on Menu items?
        return True
        
    @property
    def label(self):
        """
        Use this in your templates instead of title as some pre-processing occurs.
        """
        if self.title:
            return self.translation.title
        
        # We've got a target, return its title
        t = self.target.object
        if isinstance(t, Content):
            return t.text_headline
        elif isinstance(t, Account):
            return t.screen_name
                
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

    
    
    