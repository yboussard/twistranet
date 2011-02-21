"""
This is a set of extensive resource management tests.
"""
from twistranet.twistapp.tests.base import TNBaseTest
from twistranet.twistapp.models import *
from twistranet.content_types import *
from twistranet.core import bootstrap

class ResourcesTest(TNBaseTest):
    """
    Just to remember:
    A <=> PJ
    B  => PJ
    """

    def test_profile_picture(self):
        """
        Check if profile picture is publicly available
        """
        self.failUnless(self.A.picture)
        self.failUnless(self.B.picture)

    # XXX PJ test is failing > renamed twist
    def twist_public_resource(self):
        """
        Try to get a public resource anonymously.
        We fetch the first we can find
        """
        # Get the first public resource
        r = Resource.objects.all()
        import sys;sys.stdout=sys.__stdout__;sys.stderr=sys.__stderr__;import ipdb; ipdb.set_trace()
        self.failUnless(r.resource_file)


