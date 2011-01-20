# -*- coding: utf-8 -*-
"""
Sample building script for the COGIP example.
"""
import csv
import os

from twistranet.twistranet.models import *
from twistranet.content_types.models import *
from twistranet.twistranet.lib.python_fixture import Fixture
from twistranet.twistranet.lib.slugify import slugify
from twistranet.twistranet.lib.log import *
from django.contrib.auth.models import User
from django.core.files import File as DjangoFile

HERE_COGIP = os.path.abspath(os.path.dirname(__file__))

def get_cogip_fixtures():
    # Just to be sure, we log as system account
    __account__ = SystemAccount.get()
    FIXTURES = []

    # Import the whole file, creating all needed fixtures, including Service as communities.
    f = open(os.path.join(HERE_COGIP, "cogip.csv"), "rU")
    c = csv.DictReader(f, delimiter = ';', fieldnames = ['index', 'firstname', 'lastname', 'sex', 'service', 'function', 'email', 'picture_file'])
    services = []
    for useraccount in c:
        # Create the user if necessary (still have to do this by hand)
        username = slugify("%s%s" % (useraccount['firstname'][0], useraccount['lastname'], ))
        username = username.lower()
        password = slugify(useraccount['lastname']).lower()
        if not User.objects.filter(username = username).exists():
            u = User.objects.create(
                username = username,
                email = useraccount['email'],
            )
            u.set_password(password)
            u.save()
        
        # Create the user account
        Fixture(
            UserAccount,
            slug = username,
            title = "%s %s" % (useraccount['firstname'], useraccount['lastname'], ),
    		description = useraccount['function'],
            permissions = "public",
            user = User.objects.get(username = username),
            force_update = True,
        ).apply()
        
        # Create a community matching user's service or make him join the service
        service_slug = slugify(useraccount['service'])
        if not service_slug in services:
            services.append(service_slug)
            Fixture(
                Community,
                slug = service_slug,
                title = useraccount['service'],
                permissions = "workgroup",
                logged_account = username,
                force_update = True,
            ).apply()
        else:
            Community.objects.get(slug = service_slug).join(UserAccount.objects.get(slug = username))

        # Create / Replace the profile picture
        picture_slug = slugify("pict_%s" % useraccount['picture_file'])
        Resource.objects.filter(slug = picture_slug).delete()
        source_fn = os.path.join(HERE_COGIP, useraccount['picture_file'])
        r = Resource(
            publisher = UserAccount.objects.get(slug = username),
            resource_file = DjangoFile(open(source_fn, "rb"), useraccount['picture_file']),
            slug = picture_slug,
        )
        r.save()
        u = UserAccount.objects.get(slug = username)
        u.picture = Resource.objects.get(slug = picture_slug)
        u.save()

    return FIXTURES


def load_cogip():
    """
    Load all the COGIP fixtures
    """
    # Import fixtures
    for obj in get_cogip_fixtures():
        obj.apply()
    
    # Manage relations matrix


