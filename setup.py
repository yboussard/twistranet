import os
from setuptools import setup, find_packages

version = '0.9.0-alpha'

setup(name='Twistranet',
      version=version,
      description="Twistranet - The social CMS",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
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
      keywords='Twistranet Django Social CMS',
      author='Numericube',
      author_email='support@numericube.com',
      url='http://numericube.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['twistranet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Django', 
          'django-debug-toolbar',
          'django-piston',  
          'django-haystack',
          'django-tinymce',
          'sorl-thumbnail',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      twistranet_project=twistranet.scripts.twistranet_project:create_project
      """,
      )