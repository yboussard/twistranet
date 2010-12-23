# top twistranet namespace / anything else inside 
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__) 

# Import TN settings early to populate main django settings file.
from twistranet.conf import defaults

# Register the logger
from log import *
log.debug("Twistranet loaded successfuly!")
