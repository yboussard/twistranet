
class ContentRegistryManager:
    """
    Content registry for content types.

    This is mandatory to properly generate forms.
    """
    # This holds a classname: (model, form) dictionnary
    _registry_ = {}
    
    def register(self, model_class, form_class, allow_creation = True):
        """
        Register a model class into the TwistraNet application.
        Will bind the form to the model.
        if allow_user is True, content is available for end users
        XXX TODO: Provide a way of ordering forms?
        """
        self._registry_[model_class.__name__]  = (model_class, form_class, allow_creation)
    
    def getContentFormClasses(self, publisher):
        """
        This method returns the appropriate content forms for a user seeing an account page.
        This returns a list of Form classes
        """
        from twistranet.models import Account, Community
        
        # Only return forms for publisher accounts I'm authorized to write on
        # Currently, only self or members can write on a publisher. May evolve.
        account = Account.objects._getAuthenticatedAccount()
        if publisher.object == account.object:
            return [ r[1] for r in self._registry_.values() if r[2] ]
        if isinstance(publisher.object, Community):
            # Check if I can publish for the community
            if publisher.can_publish:
                return [ r[1] for r in self._registry_.values() if r[2] ]
                
        # Else, no forms.
        return []
        
    def getModelClass(self, name):
        """
        Evident :)
        """
        return self._registry_[name][0]
        
    
ContentRegistry = ContentRegistryManager()
    
