"""
This is the content used as a notification.
"""
from django.db import models

from twistranet.twistapp.models import Account, Content
from twistranet.twistapp.lib import permissions

class Notification(Content):
    """
    ACCOUNT did WHAT [on ACCOUNT/CONTENT].
    This is an internal system message, available to people following either the first or second mentionned account.
    It's meant to be posted by SystemAccount only.

    Author is usually SystemAccount.
    Publisher is usually the community (or account) this content belongs to.
    """
    # View / permissions overriding support
    permission_templates = permissions.ephemeral_templates
    type_summary_view = "content/summary.notification.part.html"
    type_detail_view = None

    # def preprocess_html_headline(self, text = None):
    #     """
    #     XXX TODO: Translate the sentence using gettext!
    #     """
    #     from django.core.urlresolvers import reverse
    #     if self.on_who:
    #         text = "@%s %s @%s" % (self.who.slug, self.did_what, self.on_who.slug)
    #     elif self.on_what:
    #         text = "@%s %s %s" % (self.who.slug, self.did_what, self.on_what.id)
    #     else:
    #         text = "@%s" % (self.who, )
    #     return super(Notification, self).preprocess_html_headline(text)

    class Meta:
        app_label = 'twistapp'
