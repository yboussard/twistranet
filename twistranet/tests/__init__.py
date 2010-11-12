from security import SecurityTest
from content import ContentTest
from wall import SimpleTest
from resources import ResourcesTest
from account_security import AccountSecurityTest
from menu import MenuTest

all_unit_tests = ( ContentTest, 
                   SimpleTest, 
                   SecurityTest, 
                   ResourcesTest, 
                   AccountSecurityTest,
                   MenuTest )

packages_with_doctests = (twistranet.forms, )

def suite():
    suite = unittest.TestSuite()                 
    # unit tests
    for t in all_unit_tests : 
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(t))  
    # doc tests
    for pkg in packages_with_doctests :
        for module in get_modules_to_test(pkg):
            suite.addTest(doctest.DocTestSuite(module)) 
    return suite








