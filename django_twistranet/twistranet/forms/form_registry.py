from  django_twistranet.twistranet.lib.log import *

class FormRegistryManager:
    """
    Form registry for content types.
    This is mandatory to properly generate forms.
    
    XXX This model is suboptimal, we should upgrade this to a stronger and safer and faster way of working!
    """
    _registry_ = {}
    
    def register(self, form_class):
        """
        Register a model class into the TwistraNet application.
        Will bind the form to the model.
        """
        # Prepare the form itself
        from base_forms import BaseInlineForm, BaseRegularForm
        model = form_class.Meta.model
        form = {
            'model_class': model, 
            'form_class': form_class,
            'allow_inline_creation': issubclass(form_class, BaseInlineForm),
            'allow_fullpage_creation': issubclass(form_class, BaseRegularForm) and form_class.allow_creation,
            "allow_fullpage_edition": issubclass(form_class, BaseRegularForm) and form_class.allow_edition,
            'content_type': model.__name__,
            'order': len(self._registry_) + 1
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
            
            
    def getFormEntries(self, name, creation = False, edition = False):
        """
        Return the form dict used for the given model.
        Will return a dict with "creation" and "edition" keys set.
        """
        if not creation and not edition:
            raise ValueError("You must specify either creation or edition")
        if creation and edition:
            raise ValueError("You must specify either creation or edition")
        if creation:
            return [ f for f in self._registry_[name] if f['allow_fullpage_creation'] ]
        if edition:
            return [ f for f in self._registry_[name] if f['allow_fullpage_edition'] ]
            
    def getFullpageForms(self, creation = False, edition = False):
        """
        This method returns the appropriate content forms for a user (globally).
        This returns a list of Form classes
        """
        if not creation and not edition:
            raise ValueError("You must specify either creation or edition")
        if creation and edition:
            raise ValueError("You must specify either creation or edition")
        
        flat_registry = []
        for r in self._registry_.values():
            flat_registry.extend(r)
        if creation:
            registry = [ f for f in flat_registry if f['allow_fullpage_creation'] ]
        if edition:
            registry = [ f for f in flat_registry if f['allow_fullpage_edition'] ]
        return tuple(registry)

    def getInlineForms(self, publisher):
        """
        This method returns the appropriate content forms for a user seeing an account page.
        This returns a list of Form classes
        """
        # Only return forms for publisher accounts I'm authorized to write on
        ret = []
        if publisher.can_publish:
            flat_reg = []
            for v in self._registry_.values():
                for w in v:
                    flat_reg.append(w)
            flat_reg.sort(lambda x,y: cmp(x['order'], y['order']))
            for f in flat_reg:
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
    
