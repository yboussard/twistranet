# Create your views here.
from django.core.urlresolvers import reverse
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _

from twistranet.twistranet.models import Content, Account
from twistranet.twistranet.forms import form_registry
from twistranet.twistranet.lib.log import *
from twistranet.actions import *
from base_view import *

class ContentView(BaseIndividualView):
    """
    Individual Content View.
    """
    context_boxes = [
        'content/publisher.box.html',    
        'actions/context.box.html', 
        'content/metadata.box.html', 
    ]
    template = None  # Will be overridden later
    template_variables = BaseIndividualView.template_variables + [
        "content",
    ]
    model_lookup = Content
    name = "content_by_id"
        
    def get_title(self,):
        return self.content.title_or_description
        
    def prepare_view(self, *args, **kw):
        """
        Prepare community view.
        Special funny thing here: we replace content by its actual underlying object.
        This is so because of the proheminence of the 'content.text' property we won't be able to fetch otherwise.
        """
        super(ContentView, self).prepare_view(*args, **kw)
        self.content = self.content and self.content.object
        if not self.template:
            self.template = self.content.detail_view


class ContentEdit(ContentView):
    """
    Generic edit form for content.
    """
    template = "content/edit.html"
    name = "edit_content"
    category = LOCAL_ACTIONS
    
    def as_action(self):
        if self.is_model:
            if self.object.can_edit:
                return super(ContentEdit, self).as_action()

    def get_form_class(self,):
        if self.object:
            ctype = self.object.model_name
        else:
            ctype = self.content_type
        try:
            return form_registry.getFormEntries(ctype, edition = True)[0]['form_class']
        except IndexError:
            raise ValueError("No Form registered for this content type: '%s'" % ctype)

    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if not self.object:
            return _("New content")
        # We translate model_name separately!
        return _("Edit %(model_name)s") % {'model_name' : _(self.object.model_name)}


class ContentCreate(ContentEdit):
    """
    Community creation. Close to the edit class
    """
    context_boxes = []
    name = "create_content"

    def prepare_view(self, publisher_id, content_type):
        """
        We pass the content_type here.
        """
        self.publisher = Account.objects.get(id = publisher_id)
        self.initial = {"publisher": self.publisher, "publisher_id": self.publisher.id,}
        self.content_type = content_type
        super(ContentCreate, self).prepare_view(None)
        
    @property
    def breadcrumb(self,):
        """
        We override breadcrumb to always consider the publisher here.
        """
        # This should be (home, here, ):
        bc = super(ContentCreate, self).breadcrumb
        
        # We insert the publisher
        return (bc[0], (self.publisher.title, self.publisher.get_absolute_url(), ), bc[1], )
        
    def as_action(self,):
        """
        We just override the as_action() method to add the publisher information.
        And we return a list of content types to create.
        
        We can create content either on a community or on our own account.
        """
        # Try to guess where are we going to publish on.
        auth = Account.objects._getAuthenticatedAccount()
        publisher = None
        if not hasattr(self, "object"):
            publisher = auth
        elif self.object.id == auth.id:
            publisher = auth
        elif issubclass(self.object.model_class, Community):
            publisher = self.object
        elif issubclass(self.object.model_class, Content):
            # If we're looking at a content, we may try to publish on its publisher
            content_pub = self.object.publisher
            log.debug("Content pub: %s" % content_pub)
            if issubclass(content_pub.model_class, Community):
                publisher = content_pub
            elif content_pub.id == auth.id:
                publisher = auth
                
        # Ok, we've found what are we going to publish to. Let's check if we have the rights to do so.
        if not publisher or not publisher.can_publish:
            return None
            
        # Wow! We've just got to fetch the action now.
        # XXX We may need to have a content creation action register system someday.
        actions = []
        for ctype in form_registry.getFullpageForms(creation = True):
            actions.append(
                Action(
                    category = CONTENT_CREATION_ACTIONS,
                    label = _(ctype["content_type"]),
                    url = reverse(self.name, args = (publisher.id, ctype["content_type"])),
                    confirm = None,
                )
            )
        return actions

class ContentDelete(BaseObjectActionView):
    """
    Remove a content from the base
    """
    model_lookup = Content
    name = "delete_content"
    
    def get_title(self,):
        # We translate model_name separately!
        return _("Delete %(model_name)s") % {'model_name' : _(self.object.model_name)}
        
    def as_action(self,):
        if not self.is_model:
            return
        if not self.object.can_delete:
            return
        action = super(ContentDelete, self).as_action()
        action.confirm = _("Do you really want to delete '%(name)s'?<br />This action cannot be undone.") % {"name": self.object.title}
        return action

    def prepare_view(self, *args, **kw):
        super(ContentDelete, self).prepare_view(*args, **kw)
        self.redirect = self.content.publisher.get_absolute_url()
        name = self.content.title_or_description
        self.content.delete()
        messages.info(
            self.request, 
            _("'%(name)s' has been deleted." % {'name': name})
        )



