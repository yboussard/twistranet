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
		description = "A twistranet sample user",
        permissions = "public",
        user = User.objects.get(id = 2),
        picture = Resource.objects.filter(slug = "default_a_picture"),
    ),
    
    Fixture(
        UserAccount,
        slug = "B",
        title = "Bernard Dubois De La Fontaine",
		description = "A twistranet sample user",
        permissions = "listed",
        user = User.objects.get(id = 3),
        picture = Resource.objects.filter(slug = "default_b_picture"),
    ),
    
    Fixture(
        UserAccount,
        slug = "C",
        title = "Chris Williams",
		description = "A twistranet sample user who doesn't want to show you that much things.",
        permissions = "private",
        user = User.objects.get(id = 4),
        picture = Resource.objects.filter(slug = "default_b_picture"),
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "admin",
        slug = "status1",
        description = "This is a public status update",
        permissions = "public",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "admin",
        slug = "status2",
        description = "This is a network status update",
        permissions = "network",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "B",
        slug = "status3",
        description = "This is a network-only status update from B",
        permissions = "network",
    ),
    
    Fixture(
        StatusUpdate,
        logged_account = "B",
        slug = "status4",
        description = "This is a public status update from B",
        permissions = "public",
    ),
    
]


