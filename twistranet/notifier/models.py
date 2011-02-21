"""
This is the content used as a notification.
"""
import pickle

from django.db import models
from django.utils.translation import ugettext as _

from twistranet.twistapp.models import Twistable, Content
from twistranet.twistapp.lib import permissions

class Notification(Content):
    """
    ACCOUNT did WHAT [on ACCOUNT/CONTENT].
    This is an internal system message, available to people following either the first or second mentionned account.
    It's meant to be posted by SystemAccount only.

    Author is usually SystemAccount.
    Publisher is usually the community (or account) this content belongs to.
    """
    # Parameters as a dict
    _encoded_parameters = models.TextField()
    
    # Other type configuration stuff
    type_text_template_creation = None
    type_html_template_creation = None
    
    # View / permissions overriding support
    permission_templates = permissions.ephemeral_templates
    type_summary_view = "content/summary.notification.part.html"
    type_detail_view = None

    def get_parameters(self,):
        """
        Unpickle parameters
        """
        if self._encoded_parameters:
            p = self._encoded_parameters
            if isinstance(p, unicode):
                p = p.encode('ascii')
            return pickle.loads(p)
        else:
            return {}
        
    def set_parameters(self, d):
        """
        Pickle parameters
        """
        if not isinstance(d, dict):
            raise TypeError("parameters must be a dict of picklable values")
        self._encoded_parameters = pickle.dumps(d)
        
    parameters = property(get_parameters, set_parameters)
    
    @property
    def message(self,):
        """
        Print message for this notification.
        We do that by de-referencing parameters and then mixing it to the message.
        XXX HEAVILY CACHE THIS !!!
        """
        n_dict = {}
        try:
            for k,v in self.parameters.items():
                n_dict[k] = Twistable.objects.get(id = v).html_link
        except Twistable.DoesNotExist:
            return None
            
        return _(self.description) % n_dict
    
    class Meta:
        app_label = 'twistapp'
