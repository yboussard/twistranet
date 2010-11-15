import os
from setuptools import setup, find_packages

version = '1.0.0-alpha'

setup(name='Twistranet',
      version=version,
      description="Twistranet - The social CMS",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Twistranet Django Social CMS',
      author='Numericube',
      author_email='support@numericube.com',
      url='http://numericube.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'django', 
          'django-debug-toolbar',
          'django-piston',  
          # 'django-haystack', the alpha version used in twistranet is not yet released
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )