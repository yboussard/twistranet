from twistranet.forms.content_forms import BaseInlineForm, BaseRegularForm


class FormRegistryManager:
    """
    Form registry for content types.
    This is mandatory to properly generate forms.
    XXX TODO: Put most of this code into settings.py?
    """
    # This holds a {classname: {}} dictionnary
    _registry_ = {}
    
    def register(self, form_class):
        """
        Register a model class into the TwistraNet application.
        Will bind the form to the model.
        if allow_user is True, content is available for end users.
        XXX TODO: Provide a way of ordering forms?
        """
        model = form_class.Meta.model
        self._registry_[model.__name__]  = {
            'model_class': model, 
            'form_class': form_class,
            'allow_inline_creation': issubclass(form_class, BaseInlineForm),
            'allow_regular_creation': issubclass(form_class, BaseRegularForm),
            'content_type': model.__name__
            }
            
    def getFormEntry(self, name):
        """
        Return the form dict used for the given model
        """
        return self._registry_[name]
            
    def getRegularFormClasses(self):
        """
        This method returns the appropriate content forms for a user (globally).
        This returns a list of Form classes
        """
        from twistranet.models import Account, Community

        # Only return forms for publisher accounts I'm authorized to write on
        account = Account.objects._getAuthenticatedAccount()
        return [ r for r in self._registry_.values() if r['allow_regular_creation'] ]

        # Else, no forms.
        return []

    
    def getInlineFormClasses(self, publisher):
        """
        This method returns the appropriate content forms for a user seeing an account page.
        This returns a list of Form classes
        """
        from twistranet.models import Account, Community
        
        # Only return forms for publisher accounts I'm authorized to write on
        account = Account.objects._getAuthenticatedAccount()
        if publisher.can_publish:
            return [ r['form_class'] for r in self._registry_.values() if r['allow_inline_creation'] ]
                
        # Else, no forms.
        return []
        
    def getModelClass(self, name):
        """
        Evident :)
        """
        return self._registry_[name]['model_class']
        
    
form_registry = FormRegistryManager()
    
