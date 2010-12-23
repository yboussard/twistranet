
This is the TwistraNet project!

(c)2010 NumeriCube


About
=====

TwistraNet is a social CMS. That is, it is a full-featured CMS with a social focus.


Requirements
============

TwistraNet is written in PYTHON. 
It requires the Django Framework (as of writing, Django 1.2.1 is mandatory)


Installation
============

- Download and install Django from http://www.djangoproject.com/download/
- Run ./manage.py syncdb (answer 'no' to admin user creation, they're not used as of this version)
- Run ./manage.py twistranet_bootstrap
- Run ./manage.py runserver 0.0.0.0
- Point your browser to http://localhost:8000/ => You're done

There are a few users already set: "A", "B" and "admin". All three have 'azerty1234' password.

Design considerations
=====================

Most things with TwistraNet are derivated from Content objects.
Stuff which can produce content are Account objects. Thus, user profiles (but not only) are derivated account objects.

This inheritance stuff is there in case we one day move data into a cassandra-like DB.

Caveats
-------

The directory structure is nonstandard for a regular django project. This is ok for everything but models.
If you want your additional models to work, you have to:
- import them from models.__init__
- add a Meta attribute "app_label = 'twistranet'" in your model class


Hot topics
==========

SSO
----

See http://docs.djangoproject.com/en/dev/howto/auth-remote-user/ to find what we've got to do on this topic.


LDAP / ActiveDirectory
-----------------------

Twistranet works fairly well with LDAP. If you want to authenticate against LDAP, first install django-ldap-auth module,
then update your settings.py with the following information (this if for default AD install, your mileage may vary):

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = "ldap://xx.xx.xx.xx:389"
AUTH_LDAP_BIND_DN = "CN=admin,DC=my-company,DC=dom"
AUTH_LDAP_BIND_PASSWORD = "admin-password"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=Users,dc=my-company,dc=dom", ldap.SCOPE_SUBTREE, "(SAMAccountName=%(user)s)")

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


With this configuration, user data will automatically get populated from AD upon login.

Acknoledgements
================

The Menu system is derived from http://code.google.com/p/django-menu/


