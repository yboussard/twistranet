from __future__ import with_statement
import os
import re
from optparse import OptionParser
import shutil
from uuid import uuid4, uuid1

IGNORE_PATTERNS = ('.pyc','.git','.svn')

def twistranet_project():
    """
    Copies the contents of the project_template directory to a new directory
    specified as an argument to the command line.
    """
    import django_twistranet
    parser = OptionParser(
        usage = "usage: %prog [options] [<template>] <project_path>\n"
            "  where project_name is the name of the directory that will be created for your site,\n"
            "  <path> is the (optional) path where you want to install it.\n"
    )
    (options, args) = parser.parse_args()

    # Check template and path args
    if len(args) < 1:
        parser.error("project_path must be specified.")
    elif len(args) == 1:
        project_path = args[0]
        project_template = 'default'
    elif len(args) == 2:
        project_path = args[1]
        project_template = args[0]
        
    # We decompose the given path to split installdir and project_name
    project_path = os.path.abspath(project_path)
    if os.path.lexists(project_path):
        parser.error("Directory '%s' already exists. "
            "Please specify a non-existing directory." % (project_path, ))
    project_name = os.path.split(project_path)[1]
    
    # Check if project_name is correct
    try:
        eval("%s is True" % project_name)
    except SyntaxError:
        parser.error("Directory '%s' must be a valid python identifier." % project_name)
    except:
        pass
    # Ensure the given directory name doesn't clash with an existing Python
    # package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    except ValueError:
        pass # It's ok to install in the same directory ;)
    else:
        parser.error("'%s' conflicts with the name of an existing "
            "Python module and cannot be used as a project name. "
            "Please try another name." % project_name)

    # Build the project up copying over the twistranet project_template
    twist_package = __import__('django_twistranet')
    twist_package_path = os.path.dirname(os.path.abspath(twist_package.__file__))
    template_dir = os.path.join(twist_package_path, "project_templates", project_template)
    if not os.path.isdir(template_dir):
        parser.error("Template '%s' is invalid." % project_template)
    shutil.copytree(template_dir, project_path, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))
    
    # Generate variables replaced in the project files
    replacement = {
        "SECRET_KEY.*$":        "SECRET_KEY = '%s'" % (uuid1(), ),
    }
    
    # Write files, copy/replace things on-the-fly.
    settings_path = os.path.join(project_path, "local_settings.py")
    with open(settings_path, "r") as f:
        data = f.read()
    with open(settings_path, "w") as f:
        for regex, repl in replacement.items():
            data = re.sub(regex, repl, data)
        f.write(data)

if __name__ == "__main__":
    twistranet_project()
