
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
    
    def getContentFormClasses(self, user_account, wall_account):
        """
        This method returns the appropriate content forms for a user seeing an account page.
        This returns a list of Form classes
        """
        # XXX Temporary. Should perform security checks one day ;)
        return [ r[1] for r in self._registry_.values() ]
        
    def getModelClass(self, name):
        """
        Evident :)
        """
        return self._registry_[name][0]
        
    
ContentRegistry = ContentRegistryManager()
    
