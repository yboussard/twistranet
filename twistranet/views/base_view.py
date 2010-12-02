


class BaseView(object):
    """
    This is used as a foundation for our classical views.
    You can define for each class which are the boxes used on it.
    """
    
    @classmethod
    def as_view(cls, *args, **kw):
        return cls(*args, **kw)
    
    def __call__(self, request):
        """
        It's up to you to override this method.
        """
        raise NotImplementedError("You must override this method")
        