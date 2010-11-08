"""
The menu / taxonomy system for TwistraNet.

This is directly inspired from http://code.google.com/p/django-menu/

XXX TODO: Make this translatable
"""

from django.db import models
from django.utils.translation import ugettext as _
from django.core import urlresolvers


class AbstractMenuItem(object):
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


class Menu(models.Model, AbstractMenuItem):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    base_url = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Admin:
        pass
        
    class Meta:
        app_label = "twistranet"
 
    def __unicode__(self):
        return _("%s" % self.name)
 
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
 
 
 
class MenuItem(models.Model, AbstractMenuItem):
    menu = models.ForeignKey(Menu)
    order = models.IntegerField()
    title = models.CharField(max_length=100, null = True, blank = False)   # If null and a target is used, will use target's title
    slug = models.SlugField()

    # Target URL / Object / Permissions
    # XXX TODO: Make the target stuff more robust
    url_name = models.CharField(max_length=100, help_text='URL Name for Reverse Lookup, eg comments.comment_was_posted', blank=True, null=True, )
    view_path = models.CharField(max_length=100, help_text='Python Path to View to Render, eg django.contrib.admin.views.main.index', blank=True, null=True, )
    link_url = models.CharField(max_length=100, help_text='URL or URI to the content, eg /about/ or http://foo.com/', blank=True, null=True, )
    target_id = models.IntegerField(null = True)
    target_kind = models.CharField(max_length = 1)     # C for content, A for account. Anyway, use a 'target' attribute instead of those.
    
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
            self.target_id = self.target.id
            if isinstance(self.target, Content):
                self.target_kind = 'C'
            elif isinstance(self.target, Account):
                self.target_kind = 'A'
            else:
                raise AssertionError("Unknown target type")
                
        elif (not self.url_name and not self.view_path and not self.link_url):
            raise ValueError("Should have at least one target or path specified for the menu")
        
        # Call the super
        super(MenuItem, self).save(*args, **kw)

    @property
    def can_view(self):
        """
        XXX Todo: check if has can_view permission
        """
        if self.target_id:
            target = self.get_target()
            if target:
                return target.can_view
            return False    # 'cause get_target() will return None if object is not found.
            
        # XXX No target => return True. We can imagine better.
        return True
        
    @property
    def label(self):
        """
        Use this in your templates instead of title as some pre-processing occurs
        """
        if self.title:
            return self.title
        target = self.get_target()
        if target:
            if self.target_kind == 'A':
                return target.screen_name
            elif self.target_kind == 'C':
                return target.text_title
                
        # Uh oh, shouldn't reach there
        raise AssertionError("Shouldn't reach here with %s" % self.id)
    
    def get_target(self, ):
        """
        XXX TODO: Make this far more efficient.
        Here we have no less than 2 queries per menu item :(
        """
        from twistranet.models import Account, Content
        
        if self.target_id:
            if self.target_kind == 'A':
                if Account.objects.filter(id = self.target_id).exists():
                    return Account.objects.get(id = self.target_id)
            elif self.target_kind == 'C':
                if Content.objects.filter(id = self.target_id).exists():
                    return Content.objects.get(id = self.target_id)
        return None

    def get_absolute_url(self):
        # Got a target id?
        target = self.get_target()
        if target:
            return target.get_absolute_url()
                    
        # Regular path resolution
        if self.url_name:
            return urlresolvers.reverse(self.url_name)
        elif self.view_path:
            return urlresolvers.reverse(self.view_path)
        elif self.link_url:
            return self.link_url
    
    
    