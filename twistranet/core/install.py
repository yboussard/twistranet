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

    # change settings.TWISTRANET_STATIC_PATH
    module = import_module('settings')
    project_path = os.path.dirname(os.path.abspath(module.__file__))
    replacement = {
        "TWISTRANET_STATIC_PATH = .*\n": "TWISTRANET_STATIC_PATH = os.path.join(HERE, 'www', 'static')\n", 
    }
    settings_path = os.path.join(project_path, "settings.py")
    f = open(settings_path, "r")
    data = f.read()
    f = open(settings_path, "w")
    for regex, repl in replacement.items():
        data = re.sub(regex, repl, data)
    f.write(data)


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
            if not os.path.isfile(dest_file):
                shutil.copy(
                    os.path.join(source_root, root, fname),
                    dest_file,
                )
    
    log.info("The twistranet theme has been installed in your project.")
