# top twistranet namespace / anything else inside 
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
__author__ = 'numeriCube'
VERSION = (0, 9, 0)
__version__ = '.'.join(map(str, VERSION))

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__) 
