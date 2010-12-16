from __future__ import with_statement
import os
from optparse import OptionParser
import shutil
from uuid import uuid4

IGNORE_PATTERNS = ('.pyc','.git','.svn')

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
    twist_package = __import__('twistranet')
    twist_package_path = os.path.dirname(os.path.abspath(twist_package.__file__))
    shutil.copytree(os.path.join(twist_package_path, "twistscripts", "project_template"), project_path, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))
    
    # When copy_templates == True, the templates and themes dirs are copied for 
    # a possible customization
    if options.copy_templates:
        template_source_path = os.path.join(twist_package_path, "twistranet",  "templates")
        template_path = os.path.join(project_path, "templates")
        shutil.copytree(template_source_path, template_path, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))
        themes_source_path = os.path.join(twist_package_path, "themes")
        themes_path = os.path.join(project_path, "themes")
        shutil.copytree(themes_source_path, themes_path, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))


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


if __name__ == "__main__":
    create_project()
