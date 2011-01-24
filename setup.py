import os
from setuptools import setup, find_packages
from django_twistranet import VERSION, __version__

setup(name = 'Twistranet',
      version = __version__,
      description = "Twistranet - The social CMS",
      long_description = open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: "
                                            "Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",        
        ],
      keywords = 'Twistranet Enterprise Social Network',
      author = 'numeriCube',
      author_email = 'twistranet@numericube.com',
      url = 'http://numericube.com',
      license = 'GPL',
      packages = find_packages(exclude=['ez_setup']),
      namespace_packages = ['django_twistranet'],
      include_package_data = True,
      zip_safe = False,
      install_requires = [
          'Django', 
          'django-debug-toolbar',
          'django-piston',  
          'django-haystack',
          'django-tinymce',
          'sorl-thumbnail',
          # -*- Extra requirements: -*-
      ],
      entry_points = """
      # -*- Entry points: -*-
      [console_scripts]
      twistranet_project=twistranet.twistscripts.twistranet_project:create_project
      """,
      )