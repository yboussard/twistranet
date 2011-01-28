import os
from setuptools import setup, find_packages
from twistranet import VERSION, __version__

setup(name = 'django-twistranet',
      version = __version__,
      description = "twistranet - An Enterprise Social Network",
      long_description = open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = [
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
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
      packages = ['twistranet'], #find_packages(exclude=['ez_setup']),
      include_package_data = True,
      zip_safe = False,
      install_requires = [
          'Django', 
          'django-debug-toolbar',
          'django-piston',  
          'django-haystack',
          'django-tinymce',
          'django-modeltranslation',
          'sorl-thumbnail',
          # -*- Extra requirements: -*-
      ],
      entry_points = """
      # -*- Entry points: -*-
      # [console_scripts]
      # twistranet_project=twistranet.core.twistranet_project:twistranet_project
      """,
      )
