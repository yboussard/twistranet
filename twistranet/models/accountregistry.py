
class AccountRegistryManager:
    """
    Account registry for account types.

    This is mandatory to properly generate forms and bootstrap data.
    """
    # This holds a classname: (model, form) dictionnary
    _registry_ = {}
    
    def register(self, model_class, form_class = None):
        """
        Register a model class into the TwistraNet application.
        """
        self._registry_[model_class.__name__]  = (model_class, form_class, )

    def getModelClass(self, name):
        """
        Evident :)
        """
        return self._registry_[name][0]
        
    
AccountRegistry = AccountRegistryManager()
    
