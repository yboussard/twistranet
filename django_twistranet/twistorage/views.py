"""
These view handle file downlaod for TN files.
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.views.static import serve
from django.http import Http404
from twistorage.storage import Twistorage

def download(request, path):
    """
    Download the specified file with TN's file manager
    """
    # Get storage and check if path exists
    storage = Twistorage()
    if not storage.exists(path):
        raise Http404
    
    # Return the underlying file
    return serve(request, path, document_root = storage.location, show_indexes = True)

