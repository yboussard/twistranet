from __future__ import with_statement
import os
from optparse import OptionParser
from distutils.dir_util import copy_tree
from shutil import move
from uuid import uuid4


def create_project():
    """
    Copies the contents of the project_template directory to a new directory
    specified as an argument to the command line.
    """

    parser = OptionParser(usage="usage: %prog [options] project_name")
    parser.add_option("-t", "--templates", dest="copy_templates", default=False,
        action="store_true", help="Copy templates and themes to the new project")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("project_name must be specified")
    project_name = args[0]
    if project_name.startswith("-"):
        parser.error("project_name cannot start with '-'")
    project_path = os.path.join(os.getcwd(), project_name)

    # Ensure the given directory name doesn't clash with an existing Python
    # package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    else:
        parser.error("'%s' conflicts with the name of an existing "
            "Python module and cannot be used as a project name. "
            "Please try another name." % project_name)

    # Build the project up copying over the twistranet project_template 
    scripts_package = __import__('twistscripts')
    scripts_package_path = os.path.dirname(os.path.abspath(scripts_package.__file__))
    copy_tree(os.path.join(scripts_package_path, "project_template"), project_path)
    
    # When copy_templates == True, the templates and themes dirs are copied for 
    # a possible customization
    if options.copy_templates:
        template_source_path = os.path.join(scripts_package_path,"..","twistranet" ,"templates")
        template_path = os.path.join(project_path, "templates")
        copy_tree(template_source_path, template_path)
        themes_source_path = os.path.join(scripts_package_path,"..","twistranet" ,"themes")
        themes_path = os.path.join(project_path, "themes")
        copy_tree(themes_source_path, themes_path)


    # Generate a unique SECREY_KEY for the project's setttings module.
    settings_path = os.path.join(os.getcwd(), project_name, "local_settings.py")
    with open(settings_path, "r") as f:
        data = f.read()
    with open(settings_path, "w") as f:
        secret_key = "%s%s%s" % (uuid4(), uuid4(), uuid4())
        data = data.replace("%(SECRET_KEY)s", secret_key)
        if options.copy_templates:
            data = data.replace('""" ### START -t OPTION','')
            data = data.replace(' ### END -t OPTION """', '') 
        f.write(data)

    # Clean up pyc files.
    for (root, dirs, files) in os.walk(project_path, False):
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))

if __name__ == "__main__":
    create_project()
