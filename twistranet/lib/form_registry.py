
class FormRegistryManager:
    """
    Form registry for content types.
    This is mandatory to properly generate forms.
    """
    # This holds a {classname: {{}}} dictionnary
    _registry_ = {}
    
    def register(self, form_class):
        """
        Register a model class into the TwistraNet application.
        Will bind the form to the model.
        if allow_user is True, content is available for end users.
        XXX TODO: Provide a way of ordering forms?
        """
        # Prepare the form itself
        from twistranet.forms.content_forms import BaseInlineForm, BaseRegularForm
        model = form_class.Meta.model
        form = {
            'model_class': model, 
            'form_class': form_class,
            'allow_inline_creation': issubclass(form_class, BaseInlineForm),
            'allow_fullpage_creation': issubclass(form_class, BaseRegularForm),
            'content_type': model.__name__
            }

        # Avoid registering twice the same form
        registered_model = self._registry_.get(model.__name__, None)
        if not registered_model:
            self._registry_[model.__name__] = []
            registered_model = self._registry_[model.__name__]
        for f in registered_model:
            if f['form_class'].__name__ == form_class.__name__:
                return  # Already registered.
        
        # Actually register it
        registered_model.append(form)
            
            
    def getFormEntries(self, name):
        """
        Return the form dict used for the given model.
        Will return the FIRST form anyway.
        """
        return self._registry_[name]
            
    def getFullpageForms(self):
        """
        This method returns the appropriate content forms for a user (globally).
        This returns a list of Form classes
        """
        from twistranet.models import Account, Community

        account = Account.objects._getAuthenticatedAccount()
        ret = []
        for m in self._registry_.values():
            for f in m:
                if f['allow_fullpage_creation']:
                    ret.append(f)

        # Else, no forms.
        return tuple(ret)

    def getInlineForms(self, publisher):
        """
        This method returns the appropriate content forms for a user seeing an account page.
        This returns a list of Form classes
        """
        from twistranet.models import Account, Community
        
        # Only return forms for publisher accounts I'm authorized to write on
        account = Account.objects._getAuthenticatedAccount()
        ret = []
        if publisher.can_publish:
            for m in self._registry_.values():
                for f in m:
                    if f['allow_inline_creation']:
                        ret.append(f)
                
        # Else, no forms.
        return tuple(ret)
        
        
    def getModelClass(self, name):
        """
        Evident :)
        """
        return self._registry_[name]['model_class']
        
    
form_registry = FormRegistryManager()
    
