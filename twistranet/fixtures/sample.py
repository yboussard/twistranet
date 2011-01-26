# -*- coding: utf-8 -*-
"""
Some sample data in there.
"""
from twistranet.twistapp.models import *
from twistranet.content_types.models import *
from twistranet.twistapp.lib.python_fixture import Fixture
from django.contrib.auth.models import User

def create_users():
    """
    Create the 3 dummy users.
    """
    for username in ('A', 'B', 'C', ):
        if User.objects.filter(username = username).exists():
            continue
        u = User.objects.create(
            username = username,
            email = "%s@numericube.com" % (username, ),
        )
        u.set_password("dummy")
        u.save()
    
def get_fixtures():
    return [
            #         Fixture(
            #             UserAccount,
            #             slug = "admin",
            #             title = "Administrator",
            # description = "A twistranet manager",
            #             permissions = "public",
            #             user = User.objects.get(username = 'admin'),
            #             picture = Resource.objects.filter(slug = "default_admin_picture"),
            #             force_update = True,
            #         ),

        Fixture(
            UserAccount,
            slug = "a",
            title = "Albert Durand",
    		description = "I'm a senior accountant. How may I help you?",
            permissions = "public",
            user = User.objects.get(username = 'A'),
            picture = Resource.objects.filter(slug = "default_a_picture"),
            force_update = True,
        ),
    
        Fixture(
            UserAccount,
            slug = "b",
            title = "Beatrice Giraud De La Fontaine",
    		description = "I work in the sales department.",
            permissions = "private",
            user = User.objects.get(username = 'B'),
            picture = Resource.objects.filter(slug = "default_b_picture"),
            force_update = True,
        ),
    
        Fixture(
            UserAccount,
            slug = "c",
            title = "Chris Williams",
    		description = "I'm a private kind of person. Don't be surprised if I don't say too much about myself!",
            permissions = "private",
            user = User.objects.get(username = 'C'),
            picture = Resource.objects.filter(slug = "default_c_picture"),
            force_update = True,
        ),
    
        # Fixture(
        #     StatusUpdate,
        #     logged_account = "admin",
        #     slug = "status1",
        #     description = "Hi everybody! Welcome to twistranet. Hope you'll enjoy working with this platform. If you need any help, feel free to contact me!",
        #     permissions = "public",
        # ),
        #     
        # Fixture(
        #     StatusUpdate,
        #     logged_account = "admin",
        #     slug = "status2",
        #     description = "Did everybody try to fill their personal profile?",
        #     permissions = "network",
        # ),

        Fixture(
            StatusUpdate,
            logged_account = "b",
            slug = "status3",
            description = "Finalizing a long-awaited sale. Weeheee!",
            permissions = "network",
        ),
    
        Fixture(
            StatusUpdate,
            logged_account = "b",
            slug = "status4",
            description = "I've just signed yet another big contract. Many thanks to all involved!",
            permissions = "public",
        ),
    
    ]


