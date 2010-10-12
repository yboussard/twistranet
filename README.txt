
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
- Run ./manage.py runserver 0.0.0.0
- Point your browser to http://localhost:8000/ => You're done

There are a few users already set: "A", "B" and "pjgrizel". All three have 'azerty1234' password.
If you want to use them, you've got to do the following:

./manage.py shell
from twistranet.models import dbsetup
dbsetup.repair()

TODO: Improve the fixtures so that default content is properly installed and users as well.


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

