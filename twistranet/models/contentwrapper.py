from django.db.models import Q

from content import Content, ContentRegistry

class ContentWrapper:
    """
    This class is used as a pivot between an account and its related content.
    It's meant to be instanciated by the Account class and provide helper methods
    to access content information relevant to the current account.
    
    We also may have subclassed content's queryset but it seemed more efficient
    (ie. faster execution) to do explicit queries for each method.
    The drawback is that they're not chainable.  
    """
    def __init__(self, account):
        self._account = account

    @property
    def authorized(self):
        """
        Return a query set of authorized objects.
        """
        my_network = self._account.getMyNetwork()
        return Content._unsecured.filter(
            (
                # Public stuff
                # XXX TODO: Add publisher visibility check
                Q(scope = "public")
            ) | (
                # Stuff from the people in my network
                Q(scope__in = ("public", "network"), publisher__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = self._account)
            )
        )

    def bound(self, content):
        """
        Return a bound (ie. editable) content object.
        Just performs security checks to ensure account can write it.
        By now only authored content can be bound.
        XXX should add admin stuff!
        """
        if content.id is None:
            # Check new, unsaved content
            content.author = self._account
            content._bound = True
        else:
            # Check existing content
            content = self.authorized.get(id = content.id)     # May raise if not in authorized
            if content.author_id == self._account.id:
                content._bound = True

            elif content.publisher_id == self._account.id:
                content._bound = True

        return content

    def create(self, content_type, *args, **kw):
        """
        Create content and set its author internal property.
        This will return the subclassed object.
        """
        # Get/Set initial parameters
        if kw.has_key('author'):
            raise ValueError("You can't pass the 'author' parameter.")
        if kw.has_key('publisher'):
            # XXX todo: check if publisher writing is allowed
            raise ValueError("You can't pass the 'publisher' parameter now.")
        else:
            publisher = self._account
        if type(content_type) in (type(u''), type('')):
            content_type = ContentRegistry.getModelClass(content_type)
        
        # Create and bound the content type
        c = content_type(
            *args,
            author = self._account,
            publisher = self._account,
            **kw
            )
        c._bound = True
        return c

    @property
    def my(self):
        return self.authorized.filter(author = self._account)

    @property
    def followed(self):
        """
        Return content explicitly followed by the account
        """
        my_followed = self._account.getMyFollowed()
        my_network = self._account.getMyNetwork()
        return Content._unsecured.filter(
            (
                # Public stuff by the people I follow
                Q(publisher__in = my_followed, scope__in = ("public", "network"))
            ) | (
                # Public AND private stuff from the people in my network
                Q(publisher__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = self._account)
            )
        )        

    def __getattr__(self, name):
        return getattr(self.authorized, name)
