
django_twistranet.twistorage
----------------------

(c)2010-2011 NumeriCube

A twistranet-aware fs storage, with a few features:

- Provides a TwistorageField which mimics a well-known social network's upload field behavior; can seemlessly select a field or upload a new one.

- Provides a TwistFile class which is derivated from django.File AND from tn's Resource.

- Provides a Twistorage class which handles all file storage for you. Basically it's just a FilesystemStorage which has a specific location for each account (publisher). It also ensures you have the right to read the file.



