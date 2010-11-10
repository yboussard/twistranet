"""
Some sample data in there.

XXX TODO: Disable sample data uploading in the settings.py file?
"""
from twistranet.models import *
from helloworld.models import HelloWorld
from twistranet.lib.python_fixture import Fixture
from django.contrib.auth.models import User

FIXTURES = [

    Fixture(
        UserAccount,
        slug = "admin",
        screen_name = "Administrator",
		description = "A twistranet manager",
        permissions = "public",
        user = User.objects.get(id = 1),
        picture = Resource.objects.filter(slug = "default_admin_picture"),
    ),
    
    Fixture(
        UserAccount,
        slug = "A",
        screen_name = "Albert Durand",
		description = "A twistranet sample user",
        permissions = "public",
        user = User.objects.get(id = 2),
        picture = Resource.objects.filter(slug = "default_a_picture"),
    ),
    
    Fixture(
        UserAccount,
        slug = "B",
        screen_name = "Bernard Dubois De La Fontaine",
		description = "A twistranet sample user",
        permissions = "listed",
        user = User.objects.get(id = 3),
        picture = Resource.objects.filter(slug = "default_b_picture"),
    ),
    
    Fixture(
        HelloWorld,
        logged_account = "admin",
        slug = "hello1",
        permissions = "public",
    ),
    
    Fixture(
        HelloWorld,
        logged_account = "A",
        slug = "hello2",
        permissions = "public",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "admin",
        slug = "status1",
        text = "This is a public status update",
        permissions = "public",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "admin",
        slug = "status2",
        text = "This is a private status update",
        permissions = "private",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "B",
        slug = "status3",
        text = "This is a network-only status update from B",
        permissions = "network",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "B",
        slug = "status4",
        text = "This is a public status update from B",
        permissions = "public",
    ),
    
    
    
]


