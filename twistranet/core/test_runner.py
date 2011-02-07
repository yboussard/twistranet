from django.test.simple import *

def tn_get_tests(app_module):
    try:
        app_path = app_module.__name__.split('.')[:-1]
        test_module = __import__('.'.join(app_path + [TEST_MODULE]), {}, {}, TEST_MODULE)
    except ImportError, e:
        # Couldn't import tests.py. Was it due to a missing file, or
        # due to an import error in a tests.py that actually exists?
        import os.path
        from imp import find_module
        try:
            mod = find_module(TEST_MODULE, [os.path.dirname(app_module.__file__)])
        except ImportError:
            # 'tests' module doesn't exist. Move on.
            test_module = None
        else:
            # The module exists, so there must be an import error in the
            # test module itself. We don't need the module; so if the
            # module was a single file module (i.e., tests.py), close the file
            # handle returned by find_module. Otherwise, the test module
            # is a directory, and there is nothing to close.
            if mod[0]:
                mod[0].close()
            raise
        print '****************************************'
        print '************** ERROR IN TESTS : \n' + str(e)
        print '*************************************\n'

    return test_module

def tn_build_suite(app_module):
    "Create a complete Django test suite for the provided application module"
    suite = unittest.TestSuite()
    # Load unit and doctests in the models.py module. If module has
    # a suite() method, use it. Otherwise build the test suite ourselves.
    if hasattr(app_module, 'suite'):
        suite.addTest(app_module.suite())
    else:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(app_module))
        try:
            suite.addTest(doctest.DocTestSuite(app_module,
                                               checker=doctestOutputChecker,
                                               runner=DocTestRunner))
        except ValueError:
            # No doc tests in models.py
            pass

    # Check to see if a separate 'tests' module exists parallel to the
    # models module
    test_module = tn_get_tests(app_module)
    if test_module:
        # Load unit and doctests in the tests.py module. If module has
        # a suite() method, use it. Otherwise build the test suite ourselves.
        if hasattr(test_module, 'suite'):
            suite.addTest(test_module.suite())
        else:
            suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_module))
            try:
                suite.addTest(doctest.DocTestSuite(test_module,
                                                   checker=doctestOutputChecker,
                                                   runner=DocTestRunner))
            except ValueError:
                # No doc tests in tests.py
                pass
    return suite


def tn_build_test(app_name, app_module, label):
    """Construct a test case with the specified label, app_name, app_module.
    """


    #
    # First, look for TestCase instances with a name that matches
    #

    test_module = tn_get_tests(app_module)
    test_parts = label.split(app_name)[1].strip('.')
    parts = test_parts.split('.')
    TestClass = getattr(app_module, parts[0], None)

    # Couldn't find the test class in models.py; look in tests.py
    if TestClass is None:
        if test_module:
            TestClass = getattr(test_module, parts[0], None)

    try:
        if issubclass(TestClass, unittest.TestCase):
            if len(parts) == 1: # label is app.TestClass
                try:
                    return unittest.TestLoader().loadTestsFromTestCase(TestClass)
                except TypeError:
                    raise ValueError("Test label '%s' does not refer to a test class" % label)
            else: # label is app.TestClass.test_method
                return TestClass(parts[1])
    except TypeError:
        # TestClass isn't a TestClass - it must be a method or normal class
        pass

    #
    # If there isn't a TestCase, look for a doctest that matches
    #
    tests = []
    for module in app_module, test_module:
        try:
            doctests = doctest.DocTestSuite(module,
                                            checker=doctestOutputChecker,
                                            runner=DocTestRunner)
            # Now iterate over the suite, looking for doctests whose name
            # matches the pattern that was given
            for test in doctests:
                if test._dt_test.name in (
                        '%s.%s' % (module.__name__, '.'.join(parts[1:])),
                        '%s.__test__.%s' % (module.__name__, '.'.join(parts[1:]))):
                    tests.append(test)
        except ValueError:
            # No doctests found.
            pass

    # If no tests were found, then we were given a bad test label.
    if not tests:
        raise ValueError("Test label '%s' does not refer to a test" % label)

    # Construct a suite out of the tests that matched.
    return unittest.TestSuite(tests)

class TwistranetTestRunner(DjangoTestSuiteRunner):

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()

        if test_labels:
            for label in test_labels: 
                apps = get_apps()
                apps_dict = {}
                for app in apps:
                    apps_dict['.'.join(app.__name__.split('.')[:-1])] = app
                # launch test suite for one app in installed app
                if apps_dict.has_key(label):
                    suite.addTest(tn_build_suite(apps_dict[label]))
                else:
                    for app_name in apps_dict.keys():
                        # launch a specific test class for an installed app
                        if app_name in label:
                            suite.addTest(tn_build_test(app_name, apps_dict[app_name], label))
                        # launch all test suites from all installed apps starting with label 
                        elif app_name.startswith(label+'.'):
                            suite.addTest(tn_build_suite(apps_dict[app_name]))
        
        # launch all tests from settings.installed apps
        else:
            for app in get_apps():
                suite.addTest(tn_build_suite(app))

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))