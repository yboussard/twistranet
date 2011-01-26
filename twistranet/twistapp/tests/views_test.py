"""
This file is dedicated to views-like procedural tests.
You can use this to test actual procedures performances as well.

We also test # of queries
"""
from django.test import TestCase
from twistranet.twistapp.models import *
from twistranet.twistapp.lib import dbsetup
from django.test.client import Client
from django.db import connections, DEFAULT_DB_ALIAS
from django.conf import settings
import pprint

class ViewsTest(TestCase):
    
    def setUp(self):
        """
        Get A and B users
        """
        dbsetup.bootstrap()
        dbsetup.repair()
        __account__ = SystemAccount.get()
        self._system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.admin = UserAccount.objects.get(user__username = "admin").account_ptr

        # Perform admin login
        self.admin_client = Client()
        self.admin_client.post("/login/", {'username': 'admin', 'password': 'azerty1234'})
        self.B_client = Client()
        self.B_client.post("/login/", {'username': 'B', 'password': 'azerty1234'})
        
        # Enable DB debug mode to allow queries count
        settings.DEBUG = True
        
        # Massive  content creation
        # from twistranet.fixtures import heavy_load
        
        # Start counting queries (XXX Don't know why q. count doesn't work well)
        # self.q_offset = len(connection.queries)
        # print self.q_offset

    def print_query_stats(self):
        """
        Print a few start about what happened
        """
        for conn in connections.all():
            # pprint.pprint(conn.queries)
            q_dict = {}
            # print "%d queries performed in the last renderd page in %fms" % (len(conn.queries), sum([ q.get("duration", 0) for q in conn.queries ]))
            for q in conn.queries:
                sql = q.get('raw_sql', None)
                if not sql:
                    continue
                if not q_dict.get(sql, None):
                    q_dict[sql] = [q['params']]
                else:
                    q_dict[sql].append(q['params'])
            # print "Duplicate queries:"
            # pprint.pprint([ i for i in q_dict.items() if len(i[1]) > 1 ])

    def test_00_loggedin_home(self):
        """
        The homepage for logged-in people.
        Print that a few times to check performance and cache options.
        """
        self.failUnless(settings.DEBUG)
        # response = self.B_client.get("/")
        # self.failUnlessEqual(response.status_code, 200)
        for i in range(10):
            response = self.admin_client.get("/")
            self.failUnlessEqual(response.status_code, 200)
        # self.print_query_stats()

    def test_01_admin_community(self,):
        """
        The community page
        """
        # response = self.admin_client.get("/account/administrators") # XXX TODO: Follow redirect
        response = self.admin_client.get("/community/administrators/") # XXX TODO: Follow redirect
        self.failUnlessEqual(response.status_code, 200)
        # self.print_query_stats()


