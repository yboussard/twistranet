import os.path

# overload with your own settings

DEBUG = True

HERE = os.path.dirname(__file__)

# if you want to use your own theme or templates
# you can do it here

"""
THEME_NAME = "mytheme"

URL_BASE_PATH = HERE   

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "%s/themes/%s" % (HERE, THEME_NAME, ),
    "%s/templates" % (HERE, ),
)

TWISTRANET_DEFAULT_RESOURCES_DIR = "%s/themes/%s/resources" % (HERE, THEME_NAME)

"""
