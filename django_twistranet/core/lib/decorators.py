from django.contrib.auth.decorators import user_passes_test


def require_access(function=None, ):
    """
    Decorator for views that checks that either the site is visible to anonymous,
    or a user is logged in, redirecting to the log-in page if necessary.
    """
    def check_access(u):
        """
        We simply check if GlobalCommunity is visible.
        If not, then that means we certainly need a login here.
        """
        from django_twistranet.models import GlobalCommunity, AnonymousAccount
        return GlobalCommunity.objects.exists()
        # mgr = GlobalCommunity.objects
        # return not isinstance(mgr._getAuthenticatedAccount(), AnonymousAccount)
        # # XXX TODO
        # return mgr.__booster__.filter(mgr.get_public_filter() | mgr.get_network_filter()).exists()
        
    actual_decorator = user_passes_test(check_access)
    if function:
        return actual_decorator(function)
    return actual_decorator

