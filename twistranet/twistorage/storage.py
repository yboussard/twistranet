import os
import errno
import urlparse
import itertools

from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files import locks, File
from django.core.files.move import file_move_safe
from django.utils.encoding import force_unicode
from django.utils.functional import LazyObject
from django.utils.importlib import import_module
from django.utils.text import get_valid_filename
from django.utils._os import safe_join

from django.core.files.storage import FileSystemStorage

import settings

class Twistorage(FileSystemStorage):
    """
    The Twistorage gives you a way to make upload/download of files
    work smoothly with Twistranet.
    
    Inside the TWISTORAGE_ROOT_PATH, it creates one directory per account,
    then it places files just inside those directories.
    
    XXX TODO: Files are accessible according to the container's visibility,
    _PLUS_ POSIX permissions (TODO: POSIX PERMISSIONS!).
    This way, you can handle security both inside and outside twistranet.
    
    name is always 'publisher_id/filename'.
    base_url can't be specified: URLs will be handled by Django views. 
    """
    def __init__(self, location = None, ):
        if location is None:
            location = settings.TWISTRANET_MEDIA_ROOT
        self.location = os.path.abspath(location)
        self.base_url = None

    def _open(self, name, mode='rb'):
        return File(open(self.path(name, 'r'), mode))

    def _save(self, name, content):
        full_path = self.path(name, 'w')
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.
        while True:
            try:
                # This file has a file path that we can move.
                if hasattr(content, 'temporary_file_path'):
                    file_move_safe(content.temporary_file_path(), full_path)
                    content.close()

                # This is a normal uploadedfile that we can stream.
                else:
                    # This fun binary flag incantation makes os.open throw an
                    # OSError if the file already exists before we open it.
                    fd = os.open(full_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0))
                    try:
                        locks.lock(fd, locks.LOCK_EX)
                        for chunk in content.chunks():
                            os.write(fd, chunk)
                    finally:
                        locks.unlock(fd)
                        os.close(fd)
            except OSError, e:
                if e.errno == errno.EEXIST:
                    # Ooops, the file exists. We need a new file name.
                    name = self.get_available_name(name)
                    full_path = self.path(name, 'w')
                else:
                    raise
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)

        return name

    def delete(self, name):
        name = self.path(name, 'w')
        # If the file exists, delete it from the filesystem.
        if os.path.exists(name):
            os.remove(name)

    def exists(self, name):
        return os.path.exists(self.path(name, 'r'))

    def listdir(self, path):
        path = self.path(path, 'r')
        directories, files = [], []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                directories.append(entry)
            else:
                files.append(entry)
        return directories, files

    def path(self, name, mode = 'r'):
        """
        Try to read name from the repository.
        Mode is 'w' if write access is required, 'r' if only read access is necessary
        """
        from twistranet.twistranet.models import Account
        try:
            # Fetch account id, join with self.location.
            # This avoids having files in the 'root' section of TN.
            # Note that we de-reference TWISTRANET_MEDIA_ROOT before, so that we always work with absolute paths.
            path = safe_join(self.location, name)
            relpath = path[len(self.location) + 1:]
            account_str, fname = relpath.split(os.path.sep, 1)
            
            # Fetch the account, check rights
            try:
                account_id = int(account_str)
                account = Account.objects.get(id = account_id)
            except ValueError:
                account = Account.objects.get(slug = account_str)
            if mode == 'r':
                if not account.can_view:
                    raise SuspiciousOperation("Attempted access to '%s' denied." % name)
            elif not account.can_edit:
                raise SuspiciousOperation("Attempted access to '%s' denied." % name)
            
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)
            
        # Things are ok and check now. Return the actual path.
        return os.path.normpath(path)

    def size(self, name):
        return os.path.getsize(self.path(name, 'r'))

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace('\\', '/')
