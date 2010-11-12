import sys, settings, re, os, imp, doctest


FILES_ALREADY_RUN = ['tests.py', 'models.py']

def find_untested_modules(package):
    """ Gets all modules not already included in Django's test suite """
    files = [re.sub('\.py$', '', f) 
             for f in os.listdir(os.path.dirname(package.__file__))
             if f.endswith(".py") 
             and os.path.basename(f) not in FILES_ALREADY_RUN]
    return [imp.load_module(file, *imp.find_module(file, package.__path__))
             for file in files]



def modules_callables(module):
    return [m for m in dir(module) if callable(getattr(module, m))]

def has_doctest(docstring):
    return ">>>" in docstring

def get_modules_to_test(module) :
    modules = []
    for module in find_untested_modules(module):
        for method in modules_callables(module):
            docstring = str(getattr(module, method).__doc__)
            if has_doctest(docstring):
                print "Found doctest(s) " + module.__name__ + "." + method
                modules.append(module)
    return modules
    