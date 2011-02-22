from django.test import TestCase
from django.conf import settings
from twistranet.twistapp.models import *
from twistranet.core import bootstrap

class TNBaseTest(TestCase):
    def setUp(self):
        """
        Get A and B users
        """
        settings.TWISTRANET_IMPORT_SAMPLE_DATA = True
        # do not import cogip samples
        settings.TWISTRANET_IMPORT_COGIP = False
        bootstrap.bootstrap()
        bootstrap.repair()
        
        __account__ = SystemAccount.get()
        self.system = __account__
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.C = UserAccount.objects.get(user__username = "C").account_ptr
        self.admin = UserAccount.objects.get(user__username = "admin").account_ptr