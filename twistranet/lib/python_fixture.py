
class Fixture(object):
    """
    Used to import initial data
    """
    
    def __init__(self, model, logged_account = None, force_update = False, **kw):
        """
        logged_account is a slug
        """
        self.model = model
        self.force_update = force_update
        self.dict = kw
        self.logged_account = logged_account
        
    def apply(self,):
        """
        Create / update model. Use the 'slug' attribute to define unicity of the content.
        """
        slug = self.dict.get('slug', None)
        obj = None
        
        # Set auth if necessary
        if self.logged_account:
            from twistranet.models import Account
            __account__ = Account.objects.get(slug = self.logged_account)
        
        # Create/get object
        if slug:
            obj_q = self.model.objects.filter(slug = slug)
            if obj_q.exists():
                if not self.force_update:
                    # Object already exists and we don't want to update. Keep it that way.
                    return
                obj = obj_q.get()
        if not obj:
            obj = self.model()
            
        # Set properties & save
        for k, v in self.dict.items():
            setattr(obj, k, v)
        obj.save()

