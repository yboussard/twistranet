"""
Special context processor to handle the logged_account variable for all of TN calls.
"""
import form_registry

def security_context(request):
    """
    Retrieve the logged account and populate the variable (don't do anything with anon account by now).
    Also get the content form available.
    And get the main_menu menu manager. (XXX TODO: Cache menu items)
    """
    from twistranet.models import GlobalCommunity, Account
    ret = dict()

    # The logged-in account
    ret['logged_account'] = Account.objects._getAuthenticatedAccount()

    # Content forms
    klasses = form_registry.form_registry.getFullpageForms(creation = True)
    if klasses:
        ret['creatable_content_types'] = klasses
    
    # Various shortcuts
    ret['path'] = request.path
    ret['global_community'] = GlobalCommunity.get()
    
    return ret
    