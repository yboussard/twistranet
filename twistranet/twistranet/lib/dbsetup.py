"""
In this file you'll find functions used to load initial data in a safe and django way,
plus some tools to check and repair your DB.

See doc/DESIGN.txt for caveats about database
"""
import traceback
import os

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User
from django.db.utils import DatabaseError
from django.core.files import File
from django.core.files.base import ContentFile

from twistranet.twistranet.models import *
from twistranet.twistranet.lib import permissions

from twistranet.twistorage.storage import Twistorage

import settings

def repair():
    """
    Repair a possibly damaged database.
    For example, incomplete fixtures can be a problem; use this to repair.
    We use that before launching tests. We should one day export a well-formed test fixture...
    
    Warning: can be very slow on a normal system!
    
    Will not erase data it doesn't know how to handle.
    """
    # Login
    __account__ = SystemAccount.objects.get()
    
    # Put all Django admin users inside the first admin community
    django_admins = UserAccount.objects.filter(user__is_superuser = True)
    admin_community = AdminCommunity.objects.get()
    for user in django_admins:
        if not admin_community in user.communities:
            admin_community.join(user, is_manager = True)


def bootstrap():
    """
    Load initial data if it's not present.
    This method is SAFE, ie. it won't destroy any existing data, only add missing stuff`.
    
    This should be called every time twistranet is started!
    """
    try:
        # Let's log in.
        __account__ = SystemAccount.objects.__booster__.get()
    except:
        # Default fixture probably not installed yet. Don't do anything yet.
        print "DatabaseError while bootstraping. Your tables are probably not created yet."
        traceback.print_exc()
        return
    
    # Create default resources by associating them to the SystemAccount.
    # XXX TODO: Make this work with subdirs
    for root, dirs, files in os.walk(settings.TWISTRANET_DEFAULT_RESOURCES_DIR):
        for fname in files:
            slug = os.path.splitext(os.path.split(fname)[1])[0]
            objects = Resource.objects.filter(slug = slug)
            if objects:
                if len(objects) > 1:
                    raise IntegrityError("More than one resource with '%s' slug" % slug)
                r = objects[0]
            else:
                r = Resource()

            # Copy file to its actual location with the storage API
            storage = Twistorage()
            source_fn = os.path.join(root, fname)
            target_fn = os.path.join(__account__.slug, fname)
            # f = File(open(source_fn, "rb"))
            # storage.save(target_fn, f)
            # f.close()

            # Set pties and save
            # target_fn = os.path.join(storage.location, target_fn)
            r.resource_file = File(open(source_fn, "rb"), fname)
            r.slug = slug
            r.save()
        break   # XXX We don't handle subdirs yet.

    # Set SystemAccount picture (which is a way to check if things are working properly).
    __account__.picture = Resource.objects.get(slug = "default_tn_picture")
    __account__.save()
        
    # Now create the bootstrap / default / help fixture objects.
    # Import your fixture there, if you don't do so they may not be importable.
    from twistranet.twistranet.fixtures.bootstrap import FIXTURES as BOOTSTRAP_FIXTURES
    from twistranet.twistranet.fixtures.help_en import FIXTURES as HELP_EN_FIXTURES
    # XXX TODO: Make a fixture registry? Or fix fixture import someway?
    try:
        from twistrans.fixtures.help_fr import FIXTURES as HELP_FR_FIXTURES
        from twistrans.fixtures.bootstrap_fr import FIXTURES as BOOTSTRAP_FR_FIXTURES
    except ImportError:
        HELP_FR_FIXTURES = []
        BOOTSTRAP_FR_FIXTURES = []
        print "twistrans not installed"
        
    # Check if default profile pictures are correctly imported
    profile_picture = Resource.objects.get(slug = "default_profile_picture")
    community_picture = Resource.objects.get(slug = "default_community_picture")
    
    # Load fixtures
    for obj in BOOTSTRAP_FIXTURES:          obj.apply()

    # Special treatment for bootstrap: Set the GlobalCommunity owner = AdminCommunity
    glob = GlobalCommunity.objects.get()
    admin = AdminCommunity.objects.get()
    glob.owner = admin
    glob.publisher = glob
    glob.save()
    admin.publisher = glob
    admin.save()

    # for obj in BOOTSTRAP_FR_FIXTURES:       obj.apply()
    for obj in HELP_EN_FIXTURES:            obj.apply()
    # for obj in HELP_FR_FIXTURES:            obj.apply()
        
    # Sample data only imported if asked to in settings.py
    if settings.TWISTRANET_IMPORT_SAMPLE_DATA:
        from twistranet.twistranet.fixtures.sample import FIXTURES as SAMPLE_DATA_FIXTURES
        for obj in SAMPLE_DATA_FIXTURES:
            obj.apply()
        
        # Add relations bwn sample users
        # A <=> admin
        # B  => admin
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        A.follow(admin)
        admin.follow(A)
        B.follow(admin)

    # Repair permissions
    repair()
    

def check_consistancy():
    """
    Check DB consistancy.
    This method is SAFE (doesn't write anything) but is blocking if a problem is detected.
    """
    # XXX Check that there's 1! global community
    # XXX Check that there's 1! admin community
    
