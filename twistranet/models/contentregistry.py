
class ContentRegistryManager:
    """
    Content registry for content types.

    This is mandatory to properly generate forms.
    """
    # This holds a classname: (model, form) dictionnary
    _registry_ = {}
    
    def register(self, model_class, form_class):
        """
        Register a model class into the TwistraNet application.
        Will bind the form to the model.
        XXX TODO: Provide a way of ordering forms?
        """
        self._registry_[model_class.__name__]  = (model_class, form_class, )
    
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
            return [ r[1] for r in self._registry_.values() ]
        if isinstance(publisher.object, Community):
            # Check if I'm in the community
            if publisher.is_member():
                return [ r[1] for r in self._registry_.values() ]
                
        # Else, no forms.
        return []
        
    def getModelClass(self, name):
        """
        Evident :)
        """
        return self._registry_[name][0]
        
    
ContentRegistry = ContentRegistryManager()
    
