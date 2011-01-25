"""
In this file you'll find functions used to load initial data in a safe and django way,
plus some tools to check and repair your DB.

See doc/DESIGN.txt for caveats about database
"""
import traceback
import os
import shutil

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User
from django.db.utils import DatabaseError
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.importlib import import_module

import django_twistranet
from django_twistranet.twistranet.models import *
from django_twistranet.twistranet.lib import permissions
from django_twistranet.twistranet.lib.slugify import slugify
from django_twistranet.twistranet.lib.log import *

from django.conf import settings

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
    except SystemAccount.DoesNotExist:
        log.info("No SystemAccount available. That means this instance has never been bootstraped, so let's do it now.")
        raise RuntimeError("Please sync your databases with 'manage.py syncdb' before bootstraping.")
    except:
        # Default fixture probably not installed yet. Don't do anything yet.
        log.info("DatabaseError while bootstraping. Your tables are probably not created yet.")
        traceback.print_exc()
        return
        
    # Copy theme-defined static files into the static directory.
    # We start by importing the theme app
    theme_app = import_module(settings.TWISTRANET_THEME_APP)
    theme_app_dir = os.path.split(theme_app.__file__)[0]
    dest_root = os.path.abspath(settings.TWISTRANET_STATIC_PATH)
    source_root = os.path.abspath(os.path.join(theme_app_dir, 'static'))
    if not os.path.isdir(dest_root):
        os.makedirs(dest_root)
    for root, dirs, files in os.walk(source_root):
        relative_root = root[len(source_root) + 1:]
        for d in dirs:
            dest_dir = os.path.join(dest_root, relative_root, d)
            if not os.path.isdir(dest_dir):
                os.mkdir(dest_dir)
        for fname in files:
            dest_file = os.path.join(dest_root, relative_root, fname)
            if not os.path.isfile(dest_file):
                shutil.copy(
                    os.path.join(source_root, root, fname),
                    dest_file,
                )
        
    # Now create the bootstrap / default / help fixture objects.
    # Import your fixture there, if you don't do so they may not be importable.
    from django_twistranet.fixtures.bootstrap import FIXTURES as BOOTSTRAP_FIXTURES
    from django_twistranet.fixtures.help_en import FIXTURES as HELP_EN_FIXTURES
    # XXX TODO: Make a fixture registry? Or fix fixture import someway?
    try:
        from twistrans.fixtures.help_fr import FIXTURES as HELP_FR_FIXTURES
        from twistrans.fixtures.bootstrap_fr import FIXTURES as BOOTSTRAP_FR_FIXTURES
    except ImportError:
        HELP_FR_FIXTURES = []
        BOOTSTRAP_FR_FIXTURES = []
        log.info("twistrans not installed, translations are not installed.")
    
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

    # Create default resources by associating them to the SystemAccount and publishing them on GlobalCommunity.
    default_resources_dir = os.path.abspath(
        os.path.join(
            os.path.split(django_twistranet.__file__)[0],
            'fixtures',
            'resources',
        )
    )
    log.debug("Default res. dir: %s" % default_resources_dir)
    for root, dirs, files in os.walk(default_resources_dir):
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
            source_fn = os.path.join(root, fname)
            r.publisher = glob
            r.resource_file = File(open(source_fn, "rb"), fname)
            r.slug = slugify(slug)
            r.save()
        break   # XXX We don't handle subdirs yet.
    
    # Set SystemAccount picture (which is a way to check if things are working properly).
    __account__.picture = Resource.objects.get(slug = "default_tn_picture")
    __account__.save()

    # for obj in BOOTSTRAP_FR_FIXTURES:       obj.apply()
    for obj in HELP_EN_FIXTURES:            obj.apply()
    # for obj in HELP_FR_FIXTURES:            obj.apply()
        
    # Sample data only imported if asked to in settings.py
    if settings.TWISTRANET_IMPORT_SAMPLE_DATA:
        from django_twistranet.fixtures import sample
        sample.create_users()
        for obj in sample.get_fixtures():
            obj.apply()
        
        # Add relations bwn sample users
        # A <=> admin
        # B  => admin
        A = UserAccount.objects.get(slug = "a")
        B = UserAccount.objects.get(slug = "b")
        admin = UserAccount.objects.get(slug = "admin")
        A.follow(admin)
        admin.follow(A)
        B.follow(admin)
        
    # Import COGIP sample
    if settings.TWISTRANET_IMPORT_COGIP:
        from django_twistranet.fixtures.cogip import load_cogip
        load_cogip()

    # Repair permissions
    repair()
    

def check_consistancy():
    """
    Check DB consistancy.
    This method is SAFE (doesn't write anything) but is blocking if a problem is detected.
    """
    # XXX Check that there's 1! global community
    # XXX Check that there's 1! admin community
    
