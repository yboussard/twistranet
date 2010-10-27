"""
Special context processor to handle the logged_account variable for all of TN calls.
"""

def security_context(request):
    """
    Retrieve the logged account and populate the variable (don't do anything with anon account by now)
    """
    if request.user and hasattr(request.user, 'get_profile'):
        return (
            {
                'logged_account': request.user.get_profile(),
            }
        )

    # No user logged-in, we return an empty tuple, we've got nothing to populate.
    return ()
    