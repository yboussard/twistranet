"""
In this file you'll find functions used to load initial data in a safe and django way,
plus some tools to check and repair your DB.

See doc/DESIGN.txt for caveats about database
"""
import os
import shutil
import re

from django.utils.importlib import import_module
from django.conf import settings

import twistranet
from twistranet.twistapp.lib.log import log

def install_theme():
    """
    Copy theme in a new twistranet instance.
    Change settings of this instance
    """

    # Copy theme-defined static files into the static directory.
    # We start by importing the theme app
    theme_app = import_module(settings.TWISTRANET_THEME_APP)
    theme_app_dir = os.path.split(theme_app.__file__)[0]
    dest_root = os.path.abspath(os.path.join(settings.HERE, 'www', 'static'))
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
            shutil.copy(
                os.path.join(source_root, root, fname),
                dest_file,
            )
    
    log.info("The twistranet theme has been installed in your project.")
