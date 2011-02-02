"""
Edit this file instead of editing settings.py.
"""

#                                           #
#               Email settings              #
#                                           #

# Enter your email address here. It will be used to give you feedback about incidents,
# and will be set as admin account's primary email address.
TWISTRANET_ADMIN_EMAIL = 'your_email@domain.com'

# Account sending 'system' email
SERVER_EMAIL = "twistranet <twistranet@numericube.com>"

# SMTP relay host. Though "localhost" should work with most systems, you may have to
# specify your own, esp. if you work behind a proxy.
EMAIL_HOST = "localhost"

# Admin accounts recieve error reports. You can add additional emails here.
ADMINS = (
    ("twistranet Administrator", TWISTRANET_ADMIN_EMAIL, ),
)

#                                           #
#             LDAP / AD settings            #
#                                           #

# If you want to work with LDAP/AD, please set ENABLE_LDAP to True,
# and configure your server in this section.
# This is set to work with an Active Directory server.
# You must tweak AUTH_LDAP_USER_* and AUTH_LDAP_PROFILE_* parameters
# below if you want to work with a non-AD LDAP schema.
LDAP_ENABLED = False

# Your LDAP server IP or name and port. Default = 389
LDAP_SERVER = "xx.xx.xx.xx"

# LDAP configuration / credentials
AUTH_LDAP_USER_BASE = "ou=Users,dc=my-company,dc=com"
AUTH_LDAP_BIND_DN = "CN=admin,DC=my-company,DC=com"
AUTH_LDAP_BIND_PASSWORD = "admin-password"

#                                           #
#             I18N/L10N settings            #
#                                           #

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'America/Chicago'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# List of defined languages for twistranet. Add / comment yours if you want to,
# and you can also change order of languages here.
# See http://docs.djangoproject.com/en/dev/ref/settings/ for an explanation of what this lambda does here.
gettext = lambda s: s
LANGUAGES = (
    ('de', gettext('German')),
    ('en', gettext('English')),
    ('fr', gettext('French')),
    ('es', gettext('Spanish')),
)


#                                           #
#             GENERATED SETTINGS            #
#                                           #
# YOU NORMALLY DON'T HAVE TO EDIT ANYTHING  #
# BELOW THIS LINE !!                        #
#                                           #

# Tweak this only if you have a non-AD LDAP schema.
if LDAP_ENABLED:
    import ldap
    from django_auth_ldap.config import LDAPSearch
    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

    AUTH_LDAP_SERVER_URI = "ldap://%s" % LDAP_SERVER
    AUTH_LDAP_USER_SEARCH = LDAPSearch(AUTH_LDAP_USER_BASE, ldap.SCOPE_SUBTREE, "(SAMAccountName=%(user)s)")

    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name":   "givenName", 
        "last_name":    "sn",
        "email":        "mail",
    }

    AUTH_LDAP_PROFILE_ATTR_MAP = {
        "title":        "cn",
        "slug":         "uid",
    }
    AUTH_LDAP_ALWAYS_UPDATE_USER = True

# This is made unique by the twistranet_project script.
# Don't edit!
SECRET_KEY = "xxx"
