import doctest
from twistranet.twistapp.tests.base import TNBaseTest
from unittest import TestSuite, main
from twistranet.twistapp.models import *
from twistranet.core import bootstrap
from django.test.client import Client
from django.conf import settings

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


class FunctionalTest(TNBaseTest):

    
    def test_doctests(self):
        tests = ( 'homepage.txt',
                 )
        for test in tests:
            doctest.testfile(test)
            #suite.addTest(doctest.DocTestSuite(test, optionflags=OPTIONFLAGS))