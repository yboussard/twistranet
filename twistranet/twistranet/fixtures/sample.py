# -*- coding: utf-8 -*-
"""
Some sample data in there.
"""
from twistranet.twistranet.models import *
from twistranet.content_types.models import *
from twistranet.twistranet.lib.python_fixture import Fixture
from django.contrib.auth.models import User

FIXTURES = [
    Fixture(
        UserAccount,
        slug = "admin",
        title = "Administrator",
		description = "A twistranet manager",
        permissions = "public",
        user = User.objects.get(id = 1),
        picture = Resource.objects.filter(slug = "default_admin_picture"),
    ),

    Fixture(
        UserAccount,
        slug = "A",
        title = "Albert Durand",
		description = "I'm a senior accountant. How may I help you?",
        permissions = "public",
        user = User.objects.get(id = 2),
        picture = Resource.objects.filter(slug = "default_a_picture"),
    ),
    
    Fixture(
        UserAccount,
        slug = "B",
        title = "Beatrice Giraud De La Fontaine",
		description = "I work in the sales department.",
        permissions = "private",
        user = User.objects.get(id = 3),
        picture = Resource.objects.filter(slug = "default_b_picture"),
    ),
    
    Fixture(
        UserAccount,
        slug = "C",
        title = "Chris Williams",
		description = "I'm a private kind of person. Don't be surprised if I don't say too much about myself!",
        permissions = "private",
        user = User.objects.get(id = 4),
        picture = Resource.objects.filter(slug = "default_c_picture"),
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "admin",
        slug = "status1",
        description = "Hi everybody! Welcome to twistranet. Hope you'll enjoy working with this platform. If you need any help, feel free to contact me!",
        permissions = "public",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "admin",
        slug = "status2",
        description = "Did everybody try to fill their personal profile?",
        permissions = "network",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "B",
        slug = "status3",
        description = "Finalizing a long-awaited sale. Weeheee!",
        permissions = "network",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "B",
        slug = "status4",
        description = "I've just signed yet another big contract. Many thanks to all involved!",
        permissions = "public",
    ),
    
]


