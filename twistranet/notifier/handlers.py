"""
Notifier handlers.
Some send emails, some insert 'notification' objects in TN, etc.

We use classes instead of functions to allow inheritance between handlers.

Don't forget to connect to your signals with 'weak = False' !!
"""
import logging

from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings

from twistranet.log import log


class NotifierHandler(object):
    def __call__(self, sender, **kwargs):
        """
        This is where our handlers get called.
        Always call your parent first to populate your class instance
        and check various stuff on it.s
        """


class LogHandler(NotifierHandler):
    '''
    Just prints a log message for what it's been called for.
    '''
    def __init__(self, level = logging.DEBUG):
        self.level = level

    def __call__(self, sender, **kwargs):
        log.log(self.level, "%s %s" % (sender, kwargs))


class NotificationHandler(NotifierHandler):
    """
    This adds a Notification object just right into your twistranet site.
    It is somewhat internationalized.

    You can customize the displayed description upon class creation: the message
    will be _'ed with %(xxx)s values filled from a dictionary.
    """
    def __init__(self, owner_arg, publisher_arg, message, permissions = "public"):
        """
        Store the message for future use.
        owner_arg and publisher_arg will be used to create the underlying content.
        owner_arg defaults to SystemAccount
        publisher_arg defaults to owner arg's publisher.
        """
        self.owner_arg = owner_arg
        self.publisher_arg = publisher_arg
        self.message = message
        self.permissions = permissions

    def __call__(self, sender, **kwargs):
        """
        We add the Notification object on behalf of SystemAccount.
        """
        from twistranet.twistranet.models import Twistable
        from twistranet.twistranet.models import SystemAccount
        from twistranet.notifier.models import Notification

        # Prepare the message dict.
        # We use title_or_description on each Twistable argument to display it.
        message_dict = {}
        for param, value in kwargs.items():
            if isinstance(value, Twistable):
                message_dict[param] = value.html_link

        # We force __account__ to fake user login.
        system = SystemAccount.get()
        __account__ = system
        owner = kwargs.get(self.owner_arg, system)
        publisher = kwargs.get(self.publisher_arg, owner.publisher)
        n = Notification(
            publisher = publisher,
            owner = owner,
            title = "",
            description = self.message % message_dict,
            permissions = self.permissions,
        )
        n.save()

class MailHandler(NotifierHandler):
    """
    This is a notifier which sends an email on behalf of TwistraNet.
    So you can define recipient (but not sender, it's set system-wide),
    subject and message.
    
    Nota: recipient_arg must be an Account.
    If it's a community, it will send a message to all members,
    except if the managers_only bool is True (then it's sent to managers only).
    
    A text_template and/or html_template can be provided. They are paths to templates
    (eg. 'email/welcome.txt' and 'email/welcome.html').
    Text template is mandatory, BTW.
    
    The TEXT (and only text) template _can_ provide a Subject: xxx line AS ITS VERY FIRST LINE line.
    But the 'subject' parameter always superseeds this.
    """
    def __init__(self, recipient_arg, text_template, subject = None, html_template = None, managers_only = False):
        self.recipient_arg = recipient_arg
        self.subject = subject
        self.text_template = text_template
        self.html_template = html_template
        self.managers_only = managers_only
        
    def __call__(self, sender, **kwargs):
        """
        Generate the message itself.
        XXX TODO: Handle translation
        """
        # Fake-Login with SystemAccount so that everybody can be notified,
        # even users this current user can't list.
        from twistranet.twistranet.models import SystemAccount, Account, UserAccount, Community
        __account__ = SystemAccount.get()
        from_email = settings.SERVER_EMAIL
        
        # Load both templates and render them with kwargs context
        text_tpl = get_template(self.text_template)
        c = Context(kwargs)
        text_content = text_tpl.render(c)
        if self.html_template:
            html_tpl = get_template(self.html_template)
            html_content = html_tpl.render(c)
        else:
            html_content = None
            
        # Fetch back subject from text template
        subject = self.subject
        log.debug(text_content)
        if not subject:
            lines = [ l for l in text_content.splitlines() if l.strip() ]
            if lines:
                subject_line = lines[0].strip()
                if subject_line.startswith("Subject:"):
                    subject = subject_line[len("Subject:"):].strip()
        if not subject:
            raise ValueError("No subject provided nor 'Subject:' first line in your text template")
        
        # Handle recipient emails
        recipient = kwargs.get(self.recipient_arg, None)
        if not recipient:
            raise ValueError("Recipient must be provided as a '%s' parameter" % self.recipient_arg)
        if isinstance(recipient, UserAccount):
            to = recipient.email
            if not to:
                log.warning("Can't send email for '%s': %s doesn't have an email registered." % (sender, recipient, ))
                return
            to = [to]
        elif isinstance(recipient, Community):
            if self.managers_only:
                members = recipient.managers
            else:
                members = recipient.members
            # XXX Suboptimal for very large communities
            to = [ member.email for member in members if member.email ]
        else:
            raise ValueError("Invalid recipient: %s" % recipient)
        
        # Prepare messages
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        if html_content:
            msg.attach_alternative(html_content, "text/html")
        msg.send()
        
