from django import forms


class ContentForm(forms.ModelForm):
    """
    Abstract class to describe the basic content form
    """
    text = forms.CharField(max_length = 255)


from TwistraNet.content.models import StatusUpdate
class StatusUpdateForm(ContentForm):
    """
    The famous status update.
    """
    # subject = forms.CharField(max_length=100)
    # message = forms.CharField()
    # sender = forms.EmailField()
    # cc_myself = forms.BooleanField(required=False)
    class Meta:
        model = StatusUpdate
        fields = ('text', )


def getContentFormClass(user_account, wall_account):
    """
    This method returns the appropriate content form for a user seeing an account page.
    The form itself can be complex if many content types are enabled.
    """
    # Anyway, now we return the status update form without any question.
    return StatusUpdateForm
    
    
    