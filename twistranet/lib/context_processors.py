"""
Special context processor to handle the logged_account variable for all of TN calls.
"""
import form_registry

def security_context(request):
    """
    Retrieve the logged account and populate the variable (don't do anything with anon account by now).
    Also get the content form available
    """
    ret = dict()

    # The logged-in account
    if request.user and hasattr(request.user, 'get_profile'):
        ret['logged_account'] = request.user.get_profile()

    # Content forms
    klasses = form_registry.form_registry.getFullpageForms()
    if klasses:
        ret['creatable_content_types'] = klasses

    return ret
    