import os
import sys
import site

# add the app's directory to the PYTHONPATH
HERE = os.path.dirname(__file__)
parent = os.path.normpath(os.path.join(HERE, '..'))
sys.path.append(parent)

# Actually call instance
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'   # XXX This is BAAAD and not djangoish. Should use 'instance.settings' instead.
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

