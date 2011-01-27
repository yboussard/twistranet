
This is the TwistraNet project!

(c)2010 NumeriCube


About
=====

TwistraNet is a Social Network tailored for the enterprise. It is also a nice CMS (Content Management System) with a social focus.


Requirements
============

TwistraNet is written in PYTHON. 
It requires the Django Framework (as of writing, Django >= 1.2 is mandatory)


Installation
============

Installation - short version
-----------------------------

- Download and untar (or unzip) twistranet from http://github.com/numericube/twistranet

- cd twistranet-x.x.x

- (sudo) python ./setup.py install clean

twistranet is now installed. You can have many sites with just one twistranet installation, so you need to explicitly deploy and bootstrap your new site.

- (sudo) twistranet_project <path_to_my_new_site>

Your server should now be fully working and running on http://localhost:8000 !

If you want to start it again:

- cd <path_to_my_new_site>

- python ./manage.py runserver 0.0.0.0:8000

Installation - the Big Picture
------------------------------

Installation is in fact a 2 steps process. You must install twistranet's core features as a python library,
then you have to create a project (which is an instance of a twistranet site).

To install twistranet's core features:

- Download and install Python >= 2.4 (with setuptools)

- Download twistranet from github.com/numericube/twistranet

- Execute (as a superuser) ./setup.py install clean ; this will normally install all dependencies.

To create a new project:

- In the directory you want your website files created, type "python twistranet_project -n [<template>] <project_path>",
    where <project_path> is the name of your site (it will be created by the process) ;
    <template> is the name of the project template to deploy. Currently admitted values are:
        
    - 'default' (which is... the default value), an empty project based on sqlite;
    
    - 'cogip', a sample french-language project of a fictious company called COGIP.
    
The '-n' (or '--no-bootstrap') is an option to tell the twistranet_project script not to bootstrap it
immediately (the bootstraping process is the initial database feed).

You can do it by hand once (and only once!) with the following commands:

- Go to your <project_path>

- Review the settings.py file and local_settings.py, change to whatever suits your needs.

  Among other things, carefully choose your DATABASE scheme, your LDAP/AD settings and the 'admin' password
  that has been generated for you.

- Execute "./manage.py bootstrap" to build the database

Running Twistranet :

- Execute ./manage.py runserver 0.0.0.0 to start playing with twistranet.

- Point your browser at http://localhost:8000

Debug mode
----------

To start twistranet in DEBUG mode, just declare a TWISTRANET_DEBUG environment variable
before starting "runserver".


Running without installing
--------------------------

You can run twistranet without installing it (but you still need to install its dependencies).

This is useful if you want to work with a development version without installing it.

For example, if you want to run twistranet from the 'my_project' directory inside the twistranet source directory, do the following:

  - Download twistranet ;
  
  - Go into the twistranet directory (there should be a ./twistranet_project.py file in there) ;

  - Execute:

    - python ./twistranet_project.py my_project

    - cd my_project

    - ./manage.py bootstrap --pythonpath ../twistranet

    - ./manage.py runserver --pythonpath ../twistranet

That's it :)


Design considerations
=====================

Most things with TwistraNet are derivated from Twistable objects.
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


